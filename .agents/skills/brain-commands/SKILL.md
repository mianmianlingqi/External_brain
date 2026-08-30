---
name: brain-commands
description: Talk to an Owner's Brain through the Brain interface. Use after Init.
---

# Brain commands

The Brain is one module. Skills call it. The View only reads it. Do not invent a second interface.

## Before Init

`Seed` and `Fork` raise `NotABrain` for Brain commands. Run Init (`expand`) first.

## Init

`ask_init(target)` asks for the first Direction and Target (`local` or `server`). Server also asks for the public URL. Then it calls `expand`. `expand` writes agent secret, View secret, `agent.address`, `view.link`, and `state.json`. A second expand does not change the first Direction.

Local Target: `load(target)` restores the Brain from `.brain/`. `agent.address` is `file://`.

Server Target: `agent.address` is `{public_url}/brain` and `view.link` is `{public_url}/?secret=...`. Agents use `connect(address, agent_secret)` — do not `load` an empty local folder. `python -m brain serve <target>` listens on `0.0.0.0` and `$PORT` even before Init (`GET /health` is `ok`). Init is `POST /brain` with `method=expand` and `first_direction` (optional `public_url`). Until then Brain commands are refused. After Init, GET serves the View and POST `/brain` accepts Agent commands. The published image serves `/data`; that directory must be a volume so `serve_target` can reload the same Direction after the process restarts.

`start_view_server(brain, view_secret)` keeps a View HTTP page up. `serve(brain, view_secret, agent_secret)` also accepts Agent POSTs. The View URL includes the View secret. `?direction=` selects a Direction. Wrong View secret is 403. The page is look-only. Wrong Agent secret cannot change the Brain. The View secret cannot POST.

## Commands

- `add_direction(name)`
- `add_point(direction, name)` / `add_question(point_id, prompt, expected)` / `add_task(point_id, prompt)`
- `add_link(before_id, after_id)` — before-after only; cycles raise `CycleRejected`
- `propose_from_text(direction, text)` then `accept` / `reject` — store only after accept
- Text lines: `POINT: name`, `QUESTION: prompt @Point | expected`, `TASK: prompt @Point`, `LINK: A -> B`
- `drill_named` / `drill_from_direction` / `drill_from_plan` / `drill_task`
- `submit_answer(drill_id, answer)` — Brain Verdict for a Question
- `report_verdict(drill_id, right)` — Owner Verdict for a Task
- `update_plan(direction)` / `edit_plan(direction, point_names)`
- `review(direction)` / `graph(direction)` / `misses(direction)` / `list_directions()`

## View

`view_snapshot(brain, view_secret, provided_secret, direction=None)` lists Directions or shows Review and Graph. Wrong secret raises `ViewDenied`. No writes.
