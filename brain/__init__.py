from __future__ import annotations

from dataclasses import dataclass


class NotABrain(Exception):
    """Raised when a Fork is used as a Brain before Init."""


class Fork:
    def review(self, direction: str) -> Review:
        raise NotABrain


@dataclass(frozen=True)
class Review:
    clear: int
    not_clear: int
    misses: int
    next_plan_point: str | None


class Brain:
    def __init__(self, first_direction: str) -> None:
        self._directions = {first_direction}

    def review(self, direction: str) -> Review:
        if direction not in self._directions:
            raise KeyError(direction)
        return Review(clear=0, not_clear=0, misses=0, next_plan_point=None)


def init(first_direction: str) -> Brain:
    return Brain(first_direction)
