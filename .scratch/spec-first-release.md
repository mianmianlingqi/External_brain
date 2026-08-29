## Problem Statement

The Owner has no personal service that holds learning state for several subjects, judges Drills, keeps a Graph of Points, writes a Plan, and shows progress on a View. Today there is only a Seed (a Git template). Other Agents have no Skill contract to talk to one Brain.

## Solution

Publish a Seed. The Owner forks it and runs Init onto a Target (their machine or a server). Init confirms the first Direction, records how an Agent connects, and gives a View link and secret. After Init, a Brain exists. Agents reach it through Skills. The Brain stores Points, Questions, Tasks, Links, Verdicts, a Plan, and Misses. The Owner looks at a read-only View: Review counts plus a Graph with Clear, Open, and Blocked Points. The Owner does not Drill, accept Proposals, or edit the Plan on the View.

## User Stories

1. As an Owner, I want to fork the Seed, so that I have my own copy that is not yet a Brain.
2. As an Owner, I want to run Init, so that a Brain and a workspace appear on a Target I choose.
3. As an Owner, I want Init to ask for the first Direction, so that the Brain starts with one subject.
4. As an Owner, I want Init to ask whether the Target is my machine or a server, so that the Brain runs where I need it.
5. As an Owner, I want Init to record how an Agent connects (address and secret), so that any Agent can use the same Brain.
6. As an Owner, I want Init to give me a View link and secret, so that I can open the progress page and others cannot.
7. As an Owner, I want a Fork before Init to refuse to act as a Brain, so that I never study against an empty shell.
8. As an Owner, I want later Directions added through a Skill, so that I do not run Init again.
9. As an Owner, I want one Brain to hold several Directions, so that I do not fork once per subject.
10. As an Owner, I want to talk only through an Agent, so that I do not need a full product UI to study.
11. As an Agent, I want a Skill contract for every Brain action, so that any harness can use the same Brain.
12. As an Owner, I want to add a Point under exactly one Direction, so that each fact has one home.
13. As an Owner, I want to add a Question under exactly one Point, so that a prompt has one home and an expected answer.
14. As an Owner, I want to add a Task under exactly one Point, so that lab, oral, or portfolio work has one home.
15. As an Owner, I want to paste notes to an Agent, so that the Agent can propose Points, Questions, and Links.
16. As an Owner, I want Proposals to stay unstored until I accept them, so that a bad split does not pollute the Graph or Plan.
17. As an Owner, I want to reject a Proposal, so that nothing is written.
18. As an Owner, I want to accept a Point Proposal, so that it becomes a stored Point.
19. As an Owner, I want to accept a Question Proposal, so that it becomes a stored Question with an expected answer.
20. As an Owner, I want to accept a Link Proposal, so that the Graph gains a before-after tie.
21. As an Owner, I want a Proposal that would create a Link loop to be rejected at accept time, so that the Plan can always sort.
22. As an Owner, I want Links to mean only “learn this Point before that Point”, so that the Graph stays simple enough to plan.
23. As an Owner, I want all Questions under a Direction to be the pool, so that I do not manage named banks.
24. As an Owner, I want to start a Drill by naming a Question, so that I can practise a specific prompt.
25. As an Owner, I want to start a Drill by asking for a Question from a Direction, so that I can practise from that pool.
26. As an Owner, I want the Brain to pick a Question from the Plan, so that practice follows the next Point.
27. As an Owner, I want to submit an answer to a Question Drill, so that the Brain issues a Verdict from the expected answer.
28. As an Owner, I want to report a Verdict for a Task Drill, so that work with no expected answer can still be right or wrong.
29. As an Owner, I want a Verdict to be only right or wrong, so that I do not deal with scores.
30. As an Owner, I want different Agents to get the same Verdict for the same Question answer, so that judgement lives in the Brain.
31. As an Owner, I want a Miss to be a Question or Task whose latest Verdict is wrong, so that retry means “still wrong now”.
32. As an Owner, I want to retry Misses under a Direction as a group, so that I can work through what is still wrong.
33. As an Owner, I want a Miss to drop off when the latest Verdict is right, so that the retry list stays current.
34. As an Owner, I want an empty Point to be not Clear, so that the Plan does not skip work that has no practice yet.
35. As an Owner, I want a Point to be Clear only when it has at least one Question or Task, each has been tried, and each latest Verdict is right, so that “passed” matches practice.
36. As an Owner, I want a Point with a not-Clear before-Point to be Blocked, so that I can see I should not start it yet.
37. As an Owner, I want a Point that has items, is not Clear, and is not Blocked to be Open, so that I can see where I am mid-work.
38. As an Owner, I want to ask the Brain to update the Plan, so that order is rewritten from Verdicts and the Graph.
39. As an Owner, I want the Plan not to rewrite after every Drill, so that the list does not jump under me.
40. As an Owner, I want to edit the Plan after the Brain writes it, so that I can override order.
41. As an Owner, I want an update of the Plan to keep my edits where it still can, so that a rewrite does not wipe my choices without need.
42. As an Owner, I want the Plan to be an ordered list of Points, so that I know what to learn next, not only which Question to do.
43. As an Owner, I want the Plan to move past Clear Points, so that I am not told to relearn what I have already passed.
44. As an Owner, I want a Review for a Direction: Clear count, not-Clear count, Miss count, and the next Plan Point, so that I can act from four numbers.
45. As an Owner, I want an Agent to fetch that Review, so that I can ask “how is this subject going” in chat.
46. As an Owner, I want a View at one address, so that I pick a Direction after I open it.
47. As an Owner, I want the View to show Review numbers and the Graph with Clear, Open, and Blocked Points, so that progress is visible at a glance.
48. As an Owner, I want the View to refuse Drills, Proposal accepts, and Plan edits, so that the page stays look-only.
49. As an Owner, I want the View to refuse anyone who lacks the Init link and secret, so that my progress stays personal.
50. As an Owner, I want a second Agent to use the same Skills and the same Brain, so that I am not locked to one harness.
51. As an Owner, I want to store a Question I typed myself (not only from pasted notes), so that the pool can grow without import.
52. As an Owner, I want to store a Task I described myself, so that I can add oral or lab work without import.
53. As an Owner, I want to store a Link I stated myself, so that I can set before-after without pasted notes.
54. As an Owner, I want those direct stores to still belong to exactly one Point or Direction as defined, so that the model stays consistent.
55. As an Owner, I want a Question without an expected answer to be refused, so that the Brain can always issue a Question Verdict.
56. As an Owner, I want a Task that includes an expected answer to be refused or treated as a Question, so that the two kinds stay distinct.
57. As an Owner, I want a Graph query for a Direction, so that an Agent can describe Clear, Open, and Blocked Points and Links.
58. As an Owner, I want Init on a server Target to still produce a workspace plus a running Brain, so that remote and local expansions match.
59. As an Owner, I want Init on a local Target to still produce a workspace plus a running Brain, so that I can run without a server.
60. As an Owner, I want the Seed to ship Skills and an empty Brain shape with no Direction named, so that each Fork stays generic until Init.
61. As a later reader of the Brain, I want Exam to remain optional and unused by first-release behaviour, so that the job stays learning under a Direction.
62. As an Owner, I want “how am I doing” not to be a prose-only comment, so that I can check counts against the Graph.

## Implementation Decisions

- One module: the Brain. Its interface is the only seam. Skills and the View are adapters. Skills send commands and queries. The View only queries.
- Init is a Skill that expands a Fork onto a Target, writes connection secrets, writes the View secret, creates the first Direction, and starts the running Brain. It is not used to add later Directions.
- Persistence sits behind the Brain interface. Callers do not see how state is stored.
- Commands on the Brain interface include at least: add Direction; propose Point, Question, Link, or Task from text; accept or reject Proposal; add Point, Question, Task, or Link directly; start Drill (by id, by Direction, or from Plan); submit Question answer; report Task Verdict; list Misses; update Plan; edit Plan; query Review; query Graph.
- Accepting a Link that would cycle fails. The Graph stays a before-after order.
- Verdict for a Question is computed only inside the Brain from the stored expected answer. Agents do not supply that Verdict.
- Verdict for a Task is supplied by the Owner through an Agent. The Brain stores it.
- Clear, Open, and Blocked are derived, not stored as a free-form label the Owner types.
- The question pool is “all Questions under this Direction”. No named bank entity.
- The View is a read-only adapter: list Directions, show Review and Graph for one Direction, authenticate with the Init secret. No write commands.
- Auth for Agents and for the View uses the secrets Init recorded. First release does not add a separate account system.
- Glossary and ADRs in this repo are the source of domain words. Do not introduce 题库, 平台, or score.

## Testing Decisions

- A good test exercises only the Brain interface: given commands, assert queries (Review, Graph, Misses, Plan, Clear/Open/Blocked, Verdict). It does not inspect storage, HTML, or Skill markdown.
- Tests use an in-memory adapter behind the same interface so they stay fast and hermetic.
- Cover at least: Init-equivalent empty Brain with first Direction; accept and reject Proposal; loop Link rejected; Question Verdict from expected answer; Task Verdict from Owner; Miss latest-wrong including Tasks; empty Point not Clear; Clear rule; Blocked from a not-Clear before-Point; Plan updates only on request; Plan edit; Review counts; View-facing queries return the same Review and Graph as the Agent-facing queries.
- There is no prior test suite in this repo. These tests are the first.

## Out of Scope

- A public or third-party question store.
- Named question banks as a second container.
- Spaced repetition by calendar time.
- Binding the Brain to a required Exam.
- Answering, accepting Proposals, or editing the Plan on the View.
- A full human product (accounts, course marketplace, social).
- Percentage or graded scores.
- Related-but-unordered Graph ties.
- Auto-rewriting the Plan after every Drill.
- Treating an empty Point as Clear.
- Generating Questions without Owner accept.

## Further Notes

- Domain words: `CONTEXT.md`. Decisions: `docs/adr/0001` through `0015` (0002, 0008, 0001, 0014 superseded where marked).
- Seam agreed with the Owner: one seam, the Brain interface. Do not add a second seam for the View.
- First release is the full learning shape, not a Drill-only slice.
- After this spec, split work with `/to-tickets`. Each ticket should stay implementable through the same Brain interface.
