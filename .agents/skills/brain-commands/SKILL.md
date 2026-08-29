---
name: brain-commands
description: Talk to an Owner's Brain through the Brain interface. Use after Init.
---

# Brain commands

The Brain is one module. Skills call it. The View only reads it. Do not invent a second interface.

## Before Init

`Seed` and `Fork` raise `NotABrain` for Brain commands. Run Init (`expand`) first.

## Init

`ask_init(target)` asks for the first Direction and Target (`local` or `server`), then calls `expand`. `expand` writes agent secret, View secret, `agent.address`, `view.link`, and `state.json`. `load(target)` restores the same Brain. A second expand does not change the first Direction.

`start_view_server(brain, view_secret)` keeps a View HTTP page up. The URL includes the secret. `?direction=` selects a Direction. Wrong secret is 403. The page is look-only.

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
