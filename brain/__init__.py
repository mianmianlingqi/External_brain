from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


class NotABrain(Exception):
    """Raised when a Seed or Fork is used as a Brain before Init."""


@dataclass(frozen=True)
class Review:
    clear: int
    not_clear: int
    misses: int
    next_plan_point: str | None


@runtime_checkable
class Brain(Protocol):
    def review(self, direction: str) -> Review: ...


class Seed:
    def review(self, direction: str) -> Review:
        raise NotABrain


class Fork:
    def review(self, direction: str) -> Review:
        raise NotABrain


class MemoryBrain:
    def __init__(self, first_direction: str) -> None:
        self._direction = first_direction

    def review(self, direction: str) -> Review:
        return Review(clear=0, not_clear=0, misses=0, next_plan_point=None)


def init(first_direction: str) -> Brain:
    return MemoryBrain(first_direction)
