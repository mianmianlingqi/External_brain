import pytest

from brain import Fork, NotABrain, Seed, init


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
