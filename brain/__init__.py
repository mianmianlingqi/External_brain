from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol, runtime_checkable


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
        if point.questions or point.tasks:
            return "open"
        return "not-clear"

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


@dataclass(frozen=True)
class ViewSnapshot:
    directions: tuple[str, ...]
    review: Review | None
    graph: Graph | None


def expand(target: str, first_direction: str, kind: str = "local") -> tuple[Brain, str, str]:
    from secrets import token_urlsafe

    root = Path(target)
    brain_dir = root / ".brain"
    state = brain_dir / "state.json"
    if state.exists():
        agent_secret = (brain_dir / "agent.secret").read_text(encoding="utf-8")
        view_secret = (brain_dir / "view.secret").read_text(encoding="utf-8")
        return load(target), agent_secret, view_secret
    brain_dir.mkdir(parents=True, exist_ok=True)
    agent_secret = token_urlsafe(16)
    view_secret = token_urlsafe(16)
    (brain_dir / "agent.secret").write_text(agent_secret, encoding="utf-8")
    (brain_dir / "view.secret").write_text(view_secret, encoding="utf-8")
    (brain_dir / "direction").write_text(first_direction, encoding="utf-8")
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


def render_html(snapshot: ViewSnapshot) -> str:
    if snapshot.review is None:
        items = "".join(f"<li>{name}</li>" for name in snapshot.directions)
        return f"<html><body><ul>{items}</ul></body></html>"
    review = snapshot.review
    points = ""
    if snapshot.graph:
        points = "".join(f"<li>{p.name}:{p.state}</li>" for p in snapshot.graph.points)
    return (
        "<html><body>"
        f"<p>clear {review.clear}</p>"
        f"<p>not-clear {review.not_clear}</p>"
        f"<p>misses {review.misses}</p>"
        f"<p>next {review.next_plan_point or 'none'}</p>"
        f"<ul>{points}</ul>"
        "</body></html>"
    )

