from __future__ import annotations

import html
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol, runtime_checkable
from urllib.parse import quote


class NotABrain(Exception):
    """Raised when a Seed or Fork is used as a Brain before Init."""


class CycleRejected(Exception):
    """Raised when a Link would make a before-after loop."""


class MissingExpectedAnswer(Exception):
    """Raised when a Question is added without an expected answer."""


@dataclass(frozen=True)
class Review:
    clear: int
    not_clear: int
    misses: int
    next_plan_point: str | None


@dataclass(frozen=True)
class GraphPoint:
    name: str
    state: str


@dataclass(frozen=True)
class Graph:
    points: tuple[GraphPoint, ...]
    links: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class Proposal:
    id: str
    kind: str
    payload: dict


@dataclass(frozen=True)
class Miss:
    name: str
    kind: str


@runtime_checkable
class Brain(Protocol):
    def review(self, direction: str) -> Review: ...
    def add_direction(self, name: str) -> None: ...
    def add_point(self, direction: str, name: str) -> str: ...
    def add_question(self, point_id: str, prompt: str, expected: str) -> str: ...
    def add_task(self, point_id: str, prompt: str) -> str: ...
    def add_link(self, before_id: str, after_id: str) -> None: ...
    def drill_named(self, question_id: str) -> str: ...
    def drill_from_direction(self, direction: str) -> str: ...
    def drill_from_plan(self, direction: str) -> str: ...
    def drill_task(self, task_id: str) -> str: ...
    def drill_misses(self, direction: str) -> tuple[str, ...]: ...
    def submit_answer(self, drill_id: str, answer: str) -> bool: ...
    def report_verdict(self, drill_id: str, right: bool) -> None: ...
    def misses(self, direction: str) -> tuple[Miss, ...]: ...
    def graph(self, direction: str) -> Graph: ...
    def propose_from_text(self, direction: str, text: str) -> tuple[Proposal, ...]: ...
    def accept(self, proposal_id: str) -> None: ...
    def reject(self, proposal_id: str) -> None: ...
    def update_plan(self, direction: str) -> tuple[str, ...]: ...
    def edit_plan(self, direction: str, point_names: tuple[str, ...]) -> None: ...
    def list_directions(self) -> tuple[str, ...]: ...


class _Uninitialized:
    def __getattr__(self, name: str):
        if name.startswith("_"):
            raise AttributeError(name)
        raise NotABrain


class Seed(_Uninitialized):
    def review(self, direction: str) -> Review:
        raise NotABrain


class Fork(_Uninitialized):
    def review(self, direction: str) -> Review:
        raise NotABrain


@dataclass
class _Question:
    prompt: str
    expected: str
    latest: bool | None = None


@dataclass
class _Task:
    prompt: str
    latest: bool | None = None


@dataclass
class _Point:
    name: str
    direction: str
    questions: dict[str, _Question] = field(default_factory=dict)
    tasks: dict[str, _Task] = field(default_factory=dict)


class MemoryBrain:
    def __init__(self, first_direction: str) -> None:
        self._n = 0
        self._path: Path | None = None
        self._directions: dict[str, list[str]] = {first_direction: []}
        self._points: dict[str, _Point] = {}
        self._links: list[tuple[str, str]] = []
        self._plans: dict[str, list[str]] = {first_direction: []}
        self._plan_manual: dict[str, list[str] | None] = {first_direction: None}
        self._proposals: dict[str, Proposal] = {}
        self._drills: dict[str, tuple[str, str]] = {}

    def _id(self, prefix: str) -> str:
        self._n += 1
        return f"{prefix}-{self._n}"

    def list_directions(self) -> tuple[str, ...]:
        return tuple(self._directions)

    def add_direction(self, name: str) -> None:
        self._directions.setdefault(name, [])
        self._plans.setdefault(name, [])
        self._plan_manual.setdefault(name, None)
        self._save()

    def add_point(self, direction: str, name: str) -> str:
        pid = self._id("point")
        self._points[pid] = _Point(name=name, direction=direction)
        self._directions[direction].append(pid)
        self._save()
        return pid

    def add_question(self, point_id: str, prompt: str, expected: str) -> str:
        if not expected:
            raise MissingExpectedAnswer
        qid = self._id("question")
        self._points[point_id].questions[qid] = _Question(prompt=prompt, expected=expected)
        self._save()
        return qid

    def add_task(self, point_id: str, prompt: str) -> str:
        tid = self._id("task")
        self._points[point_id].tasks[tid] = _Task(prompt=prompt)
        self._save()
        return tid

    def _would_cycle(self, before_id: str, after_id: str) -> bool:
        adj: dict[str, list[str]] = {}
        for a, b in self._links + [(before_id, after_id)]:
            adj.setdefault(a, []).append(b)
        seen: set[str] = set()
        stack = [after_id]
        while stack:
            node = stack.pop()
            if node == before_id:
                return True
            if node in seen:
                continue
            seen.add(node)
            stack.extend(adj.get(node, []))
        return False

    def add_link(self, before_id: str, after_id: str) -> None:
        if self._would_cycle(before_id, after_id):
            raise CycleRejected
        self._links.append((before_id, after_id))
        self._save()

    def _point_clear(self, point: _Point) -> bool:
        items = list(point.questions.values()) + list(point.tasks.values())
        if not items:
            return False
        return all(item.latest is True for item in items)

    def _before_ids(self, point_id: str) -> list[str]:
        return [a for a, b in self._links if b == point_id]

    def _state(self, point_id: str) -> str:
        point = self._points[point_id]
        if any(not self._point_clear(self._points[b]) for b in self._before_ids(point_id) if b in self._points):
            return "blocked"
        if self._point_clear(point):
            return "clear"
        return "open"

    def review(self, direction: str) -> Review:
        pids = self._directions.get(direction, [])
        clear = sum(1 for p in pids if self._state(p) == "clear")
        not_clear = len(pids) - clear
        miss_count = len(self.misses(direction))
        plan = self._plans.get(direction, [])
        next_name = None
        for pid in plan:
            if self._state(pid) != "clear":
                next_name = self._points[pid].name
                break
        return Review(clear=clear, not_clear=not_clear, misses=miss_count, next_plan_point=next_name)

    def misses(self, direction: str) -> tuple[Miss, ...]:
        found: list[Miss] = []
        for pid in self._directions.get(direction, []):
            point = self._points[pid]
            for q in point.questions.values():
                if q.latest is False:
                    found.append(Miss(name=q.prompt, kind="question"))
            for t in point.tasks.values():
                if t.latest is False:
                    found.append(Miss(name=t.prompt, kind="task"))
        return tuple(found)

    def graph(self, direction: str) -> Graph:
        pids = self._directions.get(direction, [])
        points = tuple(GraphPoint(name=self._points[p].name, state=self._state(p)) for p in pids)
        links = tuple(
            (self._points[a].name, self._points[b].name)
            for a, b in self._links
            if a in pids and b in pids
        )
        return Graph(points=points, links=links)

    def drill_named(self, question_id: str) -> str:
        did = self._id("drill")
        self._drills[did] = ("question", question_id)
        return did

    def drill_from_direction(self, direction: str) -> str:
        for pid in self._directions[direction]:
            qs = self._points[pid].questions
            if qs:
                return self.drill_named(next(iter(qs)))
        raise KeyError(direction)

    def drill_from_plan(self, direction: str) -> str:
        review = self.review(direction)
        if review.next_plan_point is None:
            raise KeyError("plan")
        for pid in self._directions[direction]:
            if self._points[pid].name == review.next_plan_point:
                qs = self._points[pid].questions
                if qs:
                    return self.drill_named(next(iter(qs)))
        raise KeyError("plan")

    def drill_task(self, task_id: str) -> str:
        did = self._id("drill")
        self._drills[did] = ("task", task_id)
        return did

    def drill_misses(self, direction: str) -> tuple[str, ...]:
        drills: list[str] = []
        for pid in self._directions.get(direction, []):
            point = self._points[pid]
            for qid, question in point.questions.items():
                if question.latest is False:
                    drills.append(self.drill_named(qid))
            for tid, task in point.tasks.items():
                if task.latest is False:
                    drills.append(self.drill_task(tid))
        return tuple(drills)

    def _find_question(self, question_id: str) -> _Question:
        for point in self._points.values():
            if question_id in point.questions:
                return point.questions[question_id]
        raise KeyError(question_id)

    def _find_task(self, task_id: str) -> _Task:
        for point in self._points.values():
            if task_id in point.tasks:
                return point.tasks[task_id]
        raise KeyError(task_id)

    def submit_answer(self, drill_id: str, answer: str) -> bool:
        kind, target = self._drills[drill_id]
        if kind != "question":
            raise TypeError(kind)
        question = self._find_question(target)
        right = answer == question.expected
        question.latest = right
        self._save()
        return right

    def report_verdict(self, drill_id: str, right: bool) -> None:
        kind, target = self._drills[drill_id]
        if kind != "task":
            raise TypeError(kind)
        self._find_task(target).latest = right
        self._save()

    def propose_from_text(self, direction: str, text: str) -> tuple[Proposal, ...]:
        created: list[Proposal] = []
        for raw in text.splitlines():
            line = raw.strip()
            if not line:
                continue
            pid = self._id("proposal")
            if line.startswith("POINT:"):
                prop = Proposal(pid, "point", {"direction": direction, "name": line[6:].strip()})
            elif line.startswith("QUESTION:"):
                body = line[9:].strip()
                prompt, _, expected = body.partition("|")
                prop = Proposal(
                    pid,
                    "question",
                    {
                        "direction": direction,
                        "point": prompt.strip().split("@")[-1] if "@" in prompt else "",
                        "prompt": prompt.strip().split("@")[0].strip(),
                        "expected": expected.strip(),
                    },
                )
            elif line.startswith("TASK:"):
                body = line[5:].strip()
                prompt, _, point = body.partition("@")
                prop = Proposal(pid, "task", {"direction": direction, "point": point.strip(), "prompt": prompt.strip()})
            elif line.startswith("LINK:"):
                body = line[5:].strip()
                before, _, after = body.partition("->")
                prop = Proposal(pid, "link", {"before": before.strip(), "after": after.strip()})
            else:
                continue
            self._proposals[pid] = prop
            created.append(prop)
        return tuple(created)

    def accept(self, proposal_id: str) -> None:
        prop = self._proposals[proposal_id]
        names = {p.name: pid for pid, p in self._points.items()}
        if prop.kind == "point":
            self.add_point(prop.payload["direction"], prop.payload["name"])
        elif prop.kind == "question":
            point_id = names[prop.payload["point"]]
            self.add_question(point_id, prop.payload["prompt"], prop.payload["expected"])
        elif prop.kind == "task":
            point_id = names[prop.payload["point"]]
            self.add_task(point_id, prop.payload["prompt"])
        elif prop.kind == "link":
            self.add_link(names[prop.payload["before"]], names[prop.payload["after"]])
        self._proposals.pop(proposal_id)
        self._save()

    def reject(self, proposal_id: str) -> None:
        self._proposals.pop(proposal_id)

    def update_plan(self, direction: str) -> tuple[str, ...]:
        pids = list(self._directions[direction])
        ordered: list[str] = []
        remaining = set(pids)
        while remaining:
            ready = [p for p in remaining if all(pred not in remaining for pred in self._before_ids(p))]
            if not ready:
                ready = list(remaining)
            ready.sort(key=lambda p: self._points[p].name)
            pick = ready[0]
            remaining.remove(pick)
            if self._state(pick) != "clear":
                ordered.append(pick)
        manual = self._plan_manual.get(direction)
        if manual:
            kept = [p for p in manual if p in ordered]
            extra = [p for p in ordered if p not in kept]
            ordered = kept + extra
        self._plans[direction] = ordered
        self._save()
        return tuple(self._points[p].name for p in ordered)

    def edit_plan(self, direction: str, point_names: tuple[str, ...]) -> None:
        names = {self._points[pid].name: pid for pid in self._directions[direction]}
        self._plan_manual[direction] = [names[n] for n in point_names]
        self._plans[direction] = list(self._plan_manual[direction])
        self._save()

    def _save(self) -> None:
        if self._path is None:
            return
        self._path.write_text(json.dumps(self._dump()), encoding="utf-8")

    def _dump(self) -> dict:
        points = {
            pid: {
                "name": point.name,
                "direction": point.direction,
                "questions": {
                    qid: {"prompt": q.prompt, "expected": q.expected, "latest": q.latest}
                    for qid, q in point.questions.items()
                },
                "tasks": {tid: {"prompt": t.prompt, "latest": t.latest} for tid, t in point.tasks.items()},
            }
            for pid, point in self._points.items()
        }
        return {
            "n": self._n,
            "directions": self._directions,
            "points": points,
            "links": self._links,
            "plans": self._plans,
            "plan_manual": self._plan_manual,
        }

    @classmethod
    def from_dump(cls, data: dict, path: Path | None = None) -> MemoryBrain:
        brain = cls(next(iter(data["directions"])))
        brain._n = data["n"]
        brain._directions = {k: list(v) for k, v in data["directions"].items()}
        brain._points = {}
        for pid, raw in data["points"].items():
            point = _Point(name=raw["name"], direction=raw["direction"])
            for qid, q in raw["questions"].items():
                point.questions[qid] = _Question(q["prompt"], q["expected"], q["latest"])
            for tid, t in raw["tasks"].items():
                point.tasks[tid] = _Task(t["prompt"], t["latest"])
            brain._points[pid] = point
        brain._links = [tuple(link) for link in data["links"]]
        brain._plans = {k: list(v) for k, v in data["plans"].items()}
        brain._plan_manual = {k: (list(v) if v else None) for k, v in data["plan_manual"].items()}
        brain._path = path
        return brain


def init(first_direction: str) -> Brain:
    return MemoryBrain(first_direction)


class ViewDenied(Exception):
    """Raised when the View secret does not match."""


class AgentDenied(Exception):
    """Raised when the Agent secret does not match."""


@dataclass(frozen=True)
class ViewSnapshot:
    directions: tuple[str, ...]
    review: Review | None
    graph: Graph | None


def expand(
    target: str, first_direction: str, kind: str = "local", public_url: str | None = None
) -> tuple[Brain, str, str]:
    from secrets import token_urlsafe

    root = Path(target)
    brain_dir = root / ".brain"
    state = brain_dir / "state.json"
    if state.exists():
        agent_secret = (brain_dir / "agent.secret").read_text(encoding="utf-8")
        view_secret = (brain_dir / "view.secret").read_text(encoding="utf-8")
        return load(target), agent_secret, view_secret
    if kind == "server" and not public_url:
        raise ValueError("public_url")
    brain_dir.mkdir(parents=True, exist_ok=True)
    agent_secret = token_urlsafe(16)
    view_secret = token_urlsafe(16)
    (brain_dir / "agent.secret").write_text(agent_secret, encoding="utf-8")
    (brain_dir / "view.secret").write_text(view_secret, encoding="utf-8")
    (brain_dir / "direction").write_text(first_direction, encoding="utf-8")
    if kind == "server":
        base = public_url.rstrip("/")
        (brain_dir / "agent.address").write_text(f"{base}/brain", encoding="utf-8")
        (brain_dir / "view.link").write_text(f"{base}/?secret={view_secret}", encoding="utf-8")
    else:
        (brain_dir / "agent.address").write_text(f"file://{brain_dir.resolve()}", encoding="utf-8")
        (brain_dir / "view.link").write_text(f"/view?secret={view_secret}", encoding="utf-8")
    (brain_dir / "target").write_text(kind, encoding="utf-8")
    (root / "WORKSPACE.md").write_text("Expanded Brain workspace.\n", encoding="utf-8")
    brain = MemoryBrain(first_direction)
    brain._path = state
    brain._save()
    return brain, agent_secret, view_secret


def load(target: str) -> Brain:
    state = Path(target) / ".brain" / "state.json"
    if not state.exists():
        raise NotABrain
    data = json.loads(state.read_text(encoding="utf-8"))
    return MemoryBrain.from_dump(data, path=state)


def view_snapshot(brain: Brain, view_secret: str, provided_secret: str, direction: str | None = None) -> ViewSnapshot:
    if provided_secret != view_secret:
        raise ViewDenied
    directions = brain.list_directions()
    if direction is None:
        return ViewSnapshot(directions=directions, review=None, graph=None)
    return ViewSnapshot(
        directions=directions,
        review=brain.review(direction),
        graph=brain.graph(direction),
    )


_VIEW_CSS = """
:root{--paper:#dfe8f4;--sheet:#f4f7fb;--ink:#15243c;--mute:#5c6d86;--rule:#b7c6da;--spine:#8b1e2d;--clear:#1f6b4a;--open:#b56a12;--blocked:#6b7280;--miss:#b42318}
*{box-sizing:border-box}
html,body{margin:0;min-height:100%;background:var(--paper);color:var(--ink);font-family:"IBM Plex Sans","Noto Sans SC",sans-serif}
body{background-image:linear-gradient(90deg,transparent 47px,#c23b2e22 47px,#c23b2e22 49px,transparent 49px),repeating-linear-gradient(180deg,transparent 0,transparent 31px,var(--rule) 31px,var(--rule) 32px);background-color:#c5d2e4}
.wrap{max-width:44rem;margin:0 auto;padding:2.5rem 1.25rem 4rem}
.sheet{background:var(--sheet);border:1px solid #9aafc8;box-shadow:6px 8px 0 #15243c14;padding:1.75rem 1.5rem 2rem;position:relative}
.sheet:before{content:"";position:absolute;left:0;top:0;bottom:0;width:.55rem;background:repeating-linear-gradient(180deg,var(--spine) 0,var(--spine) 10px,transparent 10px,transparent 18px)}
.kicker{font-size:.72rem;letter-spacing:.18em;text-transform:uppercase;color:var(--mute);margin:0 0 .35rem}
h1{font-family:"Noto Serif SC","Source Han Serif SC",serif;font-weight:650;font-size:1.7rem;line-height:1.25;margin:0 0 1.25rem}
.dirs{list-style:none;padding:0;margin:0;display:grid;gap:.7rem}
.dirs a,.dirs li{display:block;padding:.85rem 1rem;border:1px solid var(--rule);background:#fff;color:var(--ink);text-decoration:none}
.dirs a:hover{border-color:var(--ink)}
.stats{display:grid;grid-template-columns:repeat(2,1fr);gap:.7rem;margin:0 0 1.4rem}
.stat{margin:0;padding:.85rem .9rem;border:1px solid var(--rule);background:#fff}
.stat b{display:block;font-size:1.6rem;font-variant-numeric:tabular-nums}
.stat span{font-size:.78rem;color:var(--mute)}
.graph{list-style:none;padding:0;margin:0;display:flex;flex-wrap:wrap;gap:.45rem}
.graph li{padding:.35rem .6rem;border:1px solid var(--rule);background:#fff;font-size:.92rem}
.graph .clear{border-color:var(--clear);color:var(--clear)}
.graph .open{border-color:var(--open);color:var(--open)}
.graph .blocked{border-color:var(--blocked);color:var(--blocked)}
.back{display:inline-block;margin-bottom:1rem;color:var(--mute);font-size:.85rem}
@media (max-width:520px){.stats{grid-template-columns:1fr}}
"""


def _view_page(title: str, body: str) -> str:
    safe_title = html.escape(title)
    return (
        "<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        f"<title>{safe_title}</title>"
        "<link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">"
        "<link rel=\"stylesheet\" href=\"https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600&family=Noto+Serif+SC:wght@650&display=swap\">"
        f"<style>{_VIEW_CSS}</style></head>"
        f"<body><main class=\"wrap\"><article class=\"sheet\">{body}</article></main></body></html>"
    )


def render_html(snapshot: ViewSnapshot, secret: str = "", direction: str | None = None) -> str:
    if snapshot.review is None:
        items = []
        for name in snapshot.directions:
            label = html.escape(name)
            if secret:
                href = f"?secret={quote(secret, safe='')}&direction={quote(name, safe='')}"
                items.append(f"<li><a href=\"{html.escape(href, quote=True)}\">{label}</a></li>")
            else:
                items.append(f"<li>{label}</li>")
        inner = (
            "<p class=\"kicker\">View</p><h1>科目</h1>"
            f"<ul class=\"dirs\">{''.join(items)}</ul>"
        )
        return _view_page("View", inner)
    review = snapshot.review
    heading = html.escape(direction or "Review")
    points = ""
    if snapshot.graph:
        chips = []
        for p in snapshot.graph.points:
            chips.append(
                f"<li class=\"{html.escape(p.state)}\">{html.escape(p.name)}:{html.escape(p.state)}</li>"
            )
        for a, b in snapshot.graph.links:
            chips.append(f"<li>{html.escape(a)}->{html.escape(b)}</li>")
        points = f"<ul class=\"graph\">{''.join(chips)}</ul>"
    back = ""
    if secret:
        back = f"<a class=\"back\" href=\"?secret={quote(secret, safe='')}\">全部科目</a>"
    inner = (
        f"{back}<p class=\"kicker\">Review</p><h1>{heading}</h1>"
        "<div class=\"stats\">"
        f"<p class=\"stat\"><b>{review.clear}</b><span>clear {review.clear}</span></p>"
        f"<p class=\"stat\"><b>{review.not_clear}</b><span>not-clear {review.not_clear}</span></p>"
        f"<p class=\"stat\"><b>{review.misses}</b><span>misses {review.misses}</span></p>"
        f"<p class=\"stat\"><b>{html.escape(review.next_plan_point or 'none')}</b><span>next {html.escape(review.next_plan_point or 'none')}</span></p>"
        "</div>"
        f"{points}"
    )
    return _view_page(direction or "Review", inner)


def ask_init(target: str, input_fn=input) -> tuple[Brain, str, str]:
    direction = input_fn("First Direction? ").strip()
    kind = input_fn("Target (local or server)? ").strip()
    if kind not in {"local", "server"}:
        raise ValueError(kind)
    if kind == "server":
        public_url = input_fn("Public URL? ").strip()
        return expand(target, direction, kind=kind, public_url=public_url)
    return expand(target, direction, kind=kind)


_BRAIN_METHODS = frozenset(
    {
        "review",
        "add_direction",
        "add_point",
        "add_question",
        "add_task",
        "add_link",
        "drill_named",
        "drill_from_direction",
        "drill_from_plan",
        "drill_task",
        "drill_misses",
        "submit_answer",
        "report_verdict",
        "misses",
        "graph",
        "propose_from_text",
        "accept",
        "reject",
        "update_plan",
        "edit_plan",
        "list_directions",
    }
)

_REMOTE_ERRORS = {
    "CycleRejected": CycleRejected,
    "MissingExpectedAnswer": MissingExpectedAnswer,
    "KeyError": KeyError,
    "TypeError": TypeError,
    "NotABrain": NotABrain,
}


def _agent_secret_from(headers: dict[str, str], body: dict) -> str:
    auth = headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:]
    return body.get("secret") or headers.get("X-Agent-Secret") or ""


def _encode_result(value):
    if value is None or isinstance(value, (bool, str, int)):
        return value
    if isinstance(value, Review):
        return {
            "clear": value.clear,
            "not_clear": value.not_clear,
            "misses": value.misses,
            "next_plan_point": value.next_plan_point,
        }
    if isinstance(value, Graph):
        return {
            "points": [{"name": p.name, "state": p.state} for p in value.points],
            "links": [list(link) for link in value.links],
        }
    if isinstance(value, Proposal):
        return {"id": value.id, "kind": value.kind, "payload": value.payload}
    if isinstance(value, Miss):
        return {"name": value.name, "kind": value.kind}
    if isinstance(value, tuple):
        return [_encode_result(item) for item in value]
    return value


def _decode_result(method: str, data):
    if method == "review":
        return Review(**data)
    if method == "graph":
        return Graph(
            points=tuple(GraphPoint(**point) for point in data["points"]),
            links=tuple(tuple(link) for link in data["links"]),
        )
    if method == "propose_from_text":
        return tuple(Proposal(item["id"], item["kind"], item["payload"]) for item in data)
    if method == "misses":
        return tuple(Miss(item["name"], item["kind"]) for item in data)
    if method in {"list_directions", "update_plan", "drill_misses"}:
        return tuple(data)
    return data


def _prepare_args(method: str, args: dict) -> dict:
    prepared = dict(args)
    if method == "edit_plan" and "point_names" in prepared:
        prepared["point_names"] = tuple(prepared["point_names"])
    return prepared


class RemoteBrain:
    def __init__(self, address: str, agent_secret: str) -> None:
        self._address = address
        self._secret = agent_secret

    def _call(self, method: str, **args):
        from urllib.error import HTTPError
        from urllib.request import Request, urlopen

        payload = json.dumps({"method": method, "args": args, "secret": self._secret}).encode("utf-8")
        req = Request(
            self._address,
            data=payload,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        try:
            with urlopen(req, timeout=30) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except HTTPError as exc:
            raw = exc.read().decode("utf-8")
            if exc.code == 403:
                raise AgentDenied from exc
            try:
                body = json.loads(raw)
            except json.JSONDecodeError:
                raise
            error = body.get("error")
            if error in _REMOTE_ERRORS:
                raise _REMOTE_ERRORS[error](body.get("message", "")) from exc
            raise
        return _decode_result(method, body.get("result"))

    def review(self, direction: str) -> Review:
        return self._call("review", direction=direction)

    def add_direction(self, name: str) -> None:
        self._call("add_direction", name=name)

    def add_point(self, direction: str, name: str) -> str:
        return self._call("add_point", direction=direction, name=name)

    def add_question(self, point_id: str, prompt: str, expected: str) -> str:
        return self._call("add_question", point_id=point_id, prompt=prompt, expected=expected)

    def add_task(self, point_id: str, prompt: str) -> str:
        return self._call("add_task", point_id=point_id, prompt=prompt)

    def add_link(self, before_id: str, after_id: str) -> None:
        self._call("add_link", before_id=before_id, after_id=after_id)

    def drill_named(self, question_id: str) -> str:
        return self._call("drill_named", question_id=question_id)

    def drill_from_direction(self, direction: str) -> str:
        return self._call("drill_from_direction", direction=direction)

    def drill_from_plan(self, direction: str) -> str:
        return self._call("drill_from_plan", direction=direction)

    def drill_task(self, task_id: str) -> str:
        return self._call("drill_task", task_id=task_id)

    def drill_misses(self, direction: str) -> tuple[str, ...]:
        return self._call("drill_misses", direction=direction)

    def submit_answer(self, drill_id: str, answer: str) -> bool:
        return self._call("submit_answer", drill_id=drill_id, answer=answer)

    def report_verdict(self, drill_id: str, right: bool) -> None:
        self._call("report_verdict", drill_id=drill_id, right=right)

    def misses(self, direction: str) -> tuple[Miss, ...]:
        return self._call("misses", direction=direction)

    def graph(self, direction: str) -> Graph:
        return self._call("graph", direction=direction)

    def propose_from_text(self, direction: str, text: str) -> tuple[Proposal, ...]:
        return self._call("propose_from_text", direction=direction, text=text)

    def accept(self, proposal_id: str) -> None:
        self._call("accept", proposal_id=proposal_id)

    def reject(self, proposal_id: str) -> None:
        self._call("reject", proposal_id=proposal_id)

    def update_plan(self, direction: str) -> tuple[str, ...]:
        return self._call("update_plan", direction=direction)

    def edit_plan(self, direction: str, point_names: tuple[str, ...]) -> None:
        self._call("edit_plan", direction=direction, point_names=list(point_names))

    def list_directions(self) -> tuple[str, ...]:
        return self._call("list_directions")


def connect(address: str, agent_secret: str) -> Brain:
    return RemoteBrain(address, agent_secret)


def serve(
    brain: Brain | None = None,
    view_secret: str = "",
    agent_secret: str = "",
    host: str = "0.0.0.0",
    port: int | None = None,
    target: str | None = None,
):
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    from threading import Lock, Thread
    from urllib.parse import parse_qs, urlparse

    if port is None:
        port = int(os.environ.get("PORT", "0"))
    lock = Lock()
    slot = {"brain": brain, "view_secret": view_secret, "agent_secret": agent_secret}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args) -> None:
            return

        def _send(self, code: int, body: bytes, content_type: str) -> None:
            self.send_response(code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path == "/health":
                self._send(200, b"ok", "text/plain; charset=utf-8")
                return
            if slot["brain"] is None:
                self._send(
                    200,
                    _view_page(
                        "View",
                        "<p class=\"kicker\">View</p><h1>尚未就绪</h1>"
                        "<p>Brain is not initialized. Run Init.</p>",
                    ).encode("utf-8"),
                    "text/html; charset=utf-8",
                )
                return
            query = parse_qs(parsed.query)
            provided = query.get("secret", [""])[0]
            direction = query.get("direction", [None])[0]
            try:
                snapshot = view_snapshot(slot["brain"], slot["view_secret"], provided, direction)
            except ViewDenied:
                self.send_error(403)
                return
            self._send(
                200,
                render_html(snapshot, provided, direction).encode("utf-8"),
                "text/html; charset=utf-8",
            )

        def do_POST(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path != "/brain":
                self.send_error(404)
                return
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length)
            try:
                payload = json.loads(raw.decode("utf-8") or "{}")
            except json.JSONDecodeError:
                self.send_error(400)
                return
            provided = _agent_secret_from({k: self.headers[k] for k in self.headers}, payload)
            method = payload.get("method", "")
            if method == "expand":
                if not target:
                    self.send_error(403)
                    return
                args = payload.get("args") or {}
                direction = (args.get("first_direction") or args.get("direction") or "").strip()
                if not direction:
                    self.send_error(400)
                    return
                with lock:
                    if slot["brain"] is not None:
                        self.send_error(409)
                        return
                    public_url = (args.get("public_url") or os.environ.get("PUBLIC_URL", "") or "http://127.0.0.1").strip()
                    _, next_agent, next_view = expand(target, direction, kind="server", public_url=public_url)
                    slot["brain"] = load(target)
                    slot["agent_secret"] = next_agent
                    slot["view_secret"] = next_view
                root = Path(target) / ".brain"
                result = {
                    "agent_secret": next_agent,
                    "view_secret": next_view,
                    "agent_address": root.joinpath("agent.address").read_text(encoding="utf-8"),
                    "view_link": root.joinpath("view.link").read_text(encoding="utf-8"),
                }
                self._send(200, json.dumps({"ok": True, "result": result}).encode("utf-8"), "application/json")
                return
            if (
                slot["brain"] is None
                or not slot["agent_secret"]
                or provided != slot["agent_secret"]
                or method not in _BRAIN_METHODS
            ):
                self.send_error(403)
                return
            args = _prepare_args(method, payload.get("args") or {})
            try:
                with lock:
                    result = getattr(slot["brain"], method)(**args)
            except Exception as exc:
                if type(exc) not in _REMOTE_ERRORS.values():
                    raise
                body = json.dumps({"ok": False, "error": type(exc).__name__, "message": str(exc)}).encode("utf-8")
                self._send(400, body, "application/json")
                return
            body = json.dumps({"ok": True, "result": _encode_result(result)}).encode("utf-8")
            self._send(200, body, "application/json")

    server = ThreadingHTTPServer((host, port), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    assigned = server.server_port
    display = "127.0.0.1" if host in {"0.0.0.0", "::"} else host
    view_url = f"http://{display}:{assigned}/?secret={slot['view_secret']}"
    agent_url = f"http://{display}:{assigned}/brain"

    def stop() -> None:
        server.shutdown()
        server.server_close()

    return view_url, agent_url, stop


def serve_target(target: str, host: str = "0.0.0.0", port: int | None = None):
    root = Path(target)
    state = root / ".brain" / "state.json"
    if state.exists():
        brain = load(target)
        agent_secret = (root / ".brain" / "agent.secret").read_text(encoding="utf-8").strip()
        view_secret = (root / ".brain" / "view.secret").read_text(encoding="utf-8").strip()
        return serve(brain, view_secret, agent_secret, host=host, port=port, target=target)
    return serve(None, "", "", host=host, port=port, target=target)


def start_view_server(brain: Brain, view_secret: str, host: str = "127.0.0.1", port: int = 0):
    view_url, _, stop = serve(brain, view_secret, "", host=host, port=port)
    return view_url, stop

