from math import sqrt
from typing import cast, overload

from numpy import array, ndarray


class FPos:
    def __init__(self, pos: tuple[float, float]) -> None:
        self._pos = pos

    @property
    def pos(self) -> tuple[float, float]:
        return self._pos

    @property
    def x(self) -> float:
        return self.pos[0]

    @property
    def y(self) -> float:
        return self.pos[1]

    def rounded(self) -> tuple[int, int]:
        return (int(self.x), int(self.y))

    @staticmethod
    def convex_combination(pos1: "FPos", pos2: "FPos", t: float) -> "FPos":
        assert 0 <= t <= 1
        x = pos1.x * t + (1 - t) * pos2.x
        y = pos1.y * t + (1 - t) * pos2.y
        return FPos((x, y))

    def to_tuple(self) -> tuple[float, float]:
        return self.pos

    def to_array(self) -> ndarray:
        return array([self.x, self.y])

    def __add__(self, other: "FPos") -> "FPos":
        return FPos((self.x + other.x, self.y + other.y))

    def __mul__(self, other: float) -> "FPos":  # scalar multiplication
        return FPos((self.x * other, self.y * other))

    def inv(self) -> "FPos":
        return self * (-1)

    def __sub__(self, other: "FPos") -> "FPos":
        return self + other.inv()

    def dot(self, other: "FPos") -> float:
        return self.x * other.x + self.y * other.y

    def norm_squared(self) -> float:
        return self.dot(self)

    def norm(self) -> float:
        return sqrt(self.norm_squared())

    def dist_squared(self, other: "FPos") -> float:
        return (other - self).norm_squared()

    def dist(self, other: "FPos") -> float:
        return (other - self).norm()

    def normalized(self) -> "FPos":
        return self * (1 / self.norm())

    def __repr__(self) -> str:
        return str(self.to_tuple())

    def __hash__(self) -> int:
        return hash(self.pos)


class Pos(FPos):
    def __init__(self, pos: tuple[int, int]) -> None:
        super().__init__(pos)

    @property
    def pos(self) -> tuple[int, int]:
        return cast(tuple[int, int], self._pos)

    @property
    def x(self) -> int:
        return self.pos[0]

    @property
    def y(self) -> int:
        return self.pos[1]

    def to_array(self) -> ndarray:
        return array([self.x, self.y])

    @overload
    def __add__(self, other: "Pos") -> "Pos": ...
    @overload
    def __add__(self, other: FPos) -> FPos: ...

    def __add__(self, other: FPos) -> FPos:
        return super().__add__(other)

    @overload
    def __mul__(self, other: int) -> "Pos": ...
    @overload
    def __mul__(self, other: float) -> FPos: ...

    def __mul__(self, other: float) -> FPos:
        return super().__mul__(other)

    @overload
    def __sub__(self, other: "Pos") -> "Pos": ...
    @overload
    def __sub__(self, other: FPos) -> FPos: ...

    def __sub__(self, other: FPos) -> FPos:
        return super().__sub__(other)

    def inv(self) -> "Pos":
        return self * (-1)
