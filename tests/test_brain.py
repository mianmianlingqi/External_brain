import pytest

from brain import CycleRejected, Fork, MissingExpectedAnswer, NotABrain, Seed, init


def test_seed_refuses_review_before_init():
    seed = Seed()
    with pytest.raises(NotABrain):
        seed.review("analog-electronics")


def test_fork_refuses_review_before_init():
    fork = Fork()
    with pytest.raises(NotABrain):
        fork.review("analog-electronics")


def test_review_of_first_direction_is_empty():
    brain = init("analog-electronics")
    review = brain.review("analog-electronics")
    assert review.clear == 0
    assert review.not_clear == 0
    assert review.misses == 0
    assert review.next_plan_point is None


def test_second_direction_has_its_own_empty_review():
    brain = init("analog-electronics")
    brain.add_direction("italian")
    analog = brain.review("analog-electronics")
    italian = brain.review("italian")
    assert analog.clear == 0
    assert italian.clear == 0
    assert analog.misses == 0
    assert italian.misses == 0


def test_second_direction_does_not_share_misses():
    brain = init("analog-electronics")
    brain.add_direction("italian")
    analog = brain.add_point("analog-electronics", "Ohm")
    q = brain.add_question(analog, "What is V?", "IR")
    brain.submit_answer(brain.drill_named(q), "no")
    assert len(brain.misses("analog-electronics")) == 1
    assert brain.misses("italian") == ()
    assert brain.review("italian").misses == 0


def test_question_without_expected_answer_is_refused():
    brain = init("analog-electronics")
    point = brain.add_point("analog-electronics", "Ohm")
    with pytest.raises(MissingExpectedAnswer):
        brain.add_question(point, "What is V?", "")


def test_brain_issues_question_verdict():
    brain = init("analog-electronics")
    point = brain.add_point("analog-electronics", "Ohm")
    question = brain.add_question(point, "What is V?", "IR")
    drill = brain.drill_named(question)
    assert brain.submit_answer(drill, "IR") is True
    assert brain.submit_answer(drill, "wrong") is False


def test_misses_can_be_drilled_as_a_group():
    brain = init("analog-electronics")
    point = brain.add_point("analog-electronics", "Ohm")
    q = brain.add_question(point, "What is V?", "IR")
    brain.submit_answer(brain.drill_named(q), "no")
    drills = brain.drill_misses("analog-electronics")
    assert len(drills) == 1
    assert brain.submit_answer(drills[0], "IR") is True
    assert brain.misses("analog-electronics") == ()


def test_latest_wrong_question_is_a_miss_then_clears():
    brain = init("analog-electronics")
    point = brain.add_point("analog-electronics", "Ohm")
    question = brain.add_question(point, "What is V?", "IR")
    drill = brain.drill_named(question)
    brain.submit_answer(drill, "wrong")
    assert len(brain.misses("analog-electronics")) == 1
    brain.submit_answer(drill, "IR")
    assert brain.misses("analog-electronics") == ()


def test_empty_point_is_not_clear_and_counts_in_review():
    brain = init("analog-electronics")
    brain.add_point("analog-electronics", "Ohm")
    review = brain.review("analog-electronics")
    assert review.clear == 0
    assert review.not_clear == 1


def test_graph_states_are_only_clear_open_or_blocked():
    brain = init("analog-electronics")
    empty = brain.add_point("analog-electronics", "Empty")
    blocked = brain.add_point("analog-electronics", "Later")
    brain.add_link(empty, blocked)
    states = {p.name: p.state for p in brain.graph("analog-electronics").points}
    assert set(states.values()) <= {"clear", "open", "blocked"}
    assert states["Empty"] == "open"
    assert states["Later"] == "blocked"


def test_point_is_clear_when_all_questions_are_latest_right():
    brain = init("analog-electronics")
    point = brain.add_point("analog-electronics", "Ohm")
    question = brain.add_question(point, "What is V?", "IR")
    brain.submit_answer(brain.drill_named(question), "IR")
    review = brain.review("analog-electronics")
    assert review.clear == 1
    assert review.not_clear == 0


def test_task_verdict_is_owner_reported_and_can_miss():
    brain = init("analog-electronics")
    point = brain.add_point("analog-electronics", "Lab")
    task = brain.add_task(point, "Build the divider")
    drill = brain.drill_task(task)
    brain.report_verdict(drill, False)
    misses = brain.misses("analog-electronics")
    assert len(misses) == 1
    assert misses[0].kind == "task"
    brain.report_verdict(drill, True)
    assert brain.misses("analog-electronics") == ()


def test_point_not_clear_while_task_still_wrong():
    brain = init("analog-electronics")
    point = brain.add_point("analog-electronics", "Lab")
    q = brain.add_question(point, "What is V?", "IR")
    t = brain.add_task(point, "Build the divider")
    brain.submit_answer(brain.drill_named(q), "IR")
    brain.report_verdict(brain.drill_task(t), False)
    assert brain.review("analog-electronics").clear == 0
    brain.report_verdict(brain.drill_task(t), True)
    assert brain.review("analog-electronics").clear == 1


def test_looping_link_is_rejected():
    brain = init("analog-electronics")
    a = brain.add_point("analog-electronics", "A")
    b = brain.add_point("analog-electronics", "B")
    brain.add_link(a, b)
    with pytest.raises(CycleRejected):
        brain.add_link(b, a)


def test_graph_marks_blocked_open_and_clear():
    brain = init("analog-electronics")
    first = brain.add_point("analog-electronics", "Ohm")
    second = brain.add_point("analog-electronics", "Kirchhoff")
    q1 = brain.add_question(first, "What is V?", "IR")
    brain.add_question(second, "KCL?", "current")
    brain.add_link(first, second)
    graph = brain.graph("analog-electronics")
    states = {p.name: p.state for p in graph.points}
    assert states["Ohm"] == "open"
    assert states["Kirchhoff"] == "blocked"
    brain.submit_answer(brain.drill_named(q1), "IR")
    states = {p.name: p.state for p in brain.graph("analog-electronics").points}
    assert states["Ohm"] == "clear"
    assert states["Kirchhoff"] == "open"


def test_drill_from_direction_uses_that_pool():
    brain = init("analog-electronics")
    brain.add_direction("italian")
    analog = brain.add_point("analog-electronics", "Ohm")
    italian = brain.add_point("italian", "Article")
    brain.add_question(analog, "What is V?", "IR")
    brain.add_question(italian, "il or la?", "il")
    drill = brain.drill_from_direction("analog-electronics")
    assert brain.submit_answer(drill, "IR") is True


def test_reject_proposal_writes_nothing():
    brain = init("analog-electronics")
    proposals = brain.propose_from_text("analog-electronics", "POINT: Ohm")
    brain.reject(proposals[0].id)
    assert brain.review("analog-electronics").not_clear == 0


def test_accept_proposals_from_text():
    brain = init("analog-electronics")
    proposals = brain.propose_from_text(
        "analog-electronics",
        "\n".join(
            [
                "POINT: Ohm",
                "POINT: Kirchhoff",
                "QUESTION: What is V? @Ohm | IR",
                "LINK: Ohm -> Kirchhoff",
            ]
        ),
    )
    for proposal in proposals:
        brain.accept(proposal.id)
    graph = brain.graph("analog-electronics")
    assert {p.name for p in graph.points} == {"Ohm", "Kirchhoff"}
    assert graph.links == (("Ohm", "Kirchhoff"),)
    assert brain.review("analog-electronics").not_clear == 2


def test_accepting_loop_link_proposal_is_rejected():
    brain = init("analog-electronics")
    for proposal in brain.propose_from_text(
        "analog-electronics",
        "POINT: A\nPOINT: B\nLINK: A -> B",
    ):
        brain.accept(proposal.id)
    looping = brain.propose_from_text("analog-electronics", "LINK: B -> A")
    with pytest.raises(CycleRejected):
        brain.accept(looping[0].id)


def test_plan_does_not_rewrite_after_drill():
    brain = init("analog-electronics")
    ohm = brain.add_point("analog-electronics", "Ohm")
    kirchhoff = brain.add_point("analog-electronics", "Kirchhoff")
    q = brain.add_question(ohm, "What is V?", "IR")
    brain.add_question(kirchhoff, "KCL?", "current")
    brain.edit_plan("analog-electronics", ("Ohm", "Kirchhoff"))
    brain.submit_answer(brain.drill_named(q), "IR")
    assert brain.review("analog-electronics").next_plan_point == "Kirchhoff"


def test_update_plan_skips_clear_and_respects_links():
    brain = init("analog-electronics")
    first = brain.add_point("analog-electronics", "Ohm")
    second = brain.add_point("analog-electronics", "Kirchhoff")
    q1 = brain.add_question(first, "What is V?", "IR")
    brain.add_question(second, "KCL?", "current")
    brain.add_link(first, second)
    brain.submit_answer(brain.drill_named(q1), "IR")
    names = brain.update_plan("analog-electronics")
    assert names == ("Kirchhoff",)
    assert brain.review("analog-electronics").next_plan_point == "Kirchhoff"


def test_edit_plan_is_kept_on_later_update():
    brain = init("analog-electronics")
    brain.add_point("analog-electronics", "Ohm")
    brain.add_point("analog-electronics", "Kirchhoff")
    brain.edit_plan("analog-electronics", ("Kirchhoff", "Ohm"))
    names = brain.update_plan("analog-electronics")
    assert names[0] == "Kirchhoff"


def test_plan_picked_drill_uses_next_point():
    brain = init("analog-electronics")
    first = brain.add_point("analog-electronics", "Ohm")
    brain.add_question(first, "What is V?", "IR")
    brain.update_plan("analog-electronics")
    drill = brain.drill_from_plan("analog-electronics")
    assert brain.submit_answer(drill, "IR") is True
