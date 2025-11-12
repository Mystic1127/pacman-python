"""Simple 2D vector math utilities used by the Pac-Man game."""

from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass
class Vector:
    """Immutable 2D vector with helpers for movement and collision math."""

    x: float
    y: float

    def __add__(self, other: "Vector") -> "Vector":
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector") -> "Vector":
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Vector":
        return Vector(self.x * scalar, self.y * scalar)

    __rmul__ = __mul__

    def distance_to(self, other: "Vector") -> float:
        dx = self.x - other.x
        dy = self.y - other.y
        return math.hypot(dx, dy)

    def normalized(self) -> "Vector":
        length = math.hypot(self.x, self.y)
        if length == 0:
            return Vector(0, 0)
        return Vector(self.x / length, self.y / length)

    def as_tuple(self) -> tuple[float, float]:
        return (self.x, self.y)

    def copy(self) -> "Vector":
        return Vector(self.x, self.y)

    def is_zero(self) -> bool:
        return self.x == 0 and self.y == 0
