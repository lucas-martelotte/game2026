from abc import ABC, abstractmethod
from typing import Protocol, TypeAlias, Union

from numpy import array, ndarray, shape

from ..essentials import FPos, Pos, Rect
from .polygon import graham_scan


class BoundedShape(ABC):

    def __init__(self) -> None:
        self._bounding_rect: Rect | None = None

    @property
    def bounding_rect(self) -> Rect:
        if not self._bounding_rect:
            self._bounding_rect = self._calculate_bounding_rect()
        return self._bounding_rect

    @abstractmethod
    def _calculate_bounding_rect(self) -> Rect: ...


class ConvexPolygonHitbox(BoundedShape):

    def __init__(self, vertices: list[FPos], ordered: bool = False) -> None:
        """
        WARNING: self.vertices should not be mutated during the
        object's lifetime since it is used for hashing.
        """
        super().__init__()
        self.vertices = vertices if ordered else graham_scan(vertices)
        self.array = array([v.to_tuple() for v in vertices])

    def _calculate_bounding_rect(self) -> Rect:
        left = min(v.x for v in self.vertices)
        right = max(v.x for v in self.vertices)
        top = min(v.y for v in self.vertices)
        bottom = max(v.y for v in self.vertices)
        return Rect(int(left), int(top), int(right - left), int(bottom - top))

    def get_outwards_direction(self, idx: int) -> FPos:
        """
        Returns the best direction pointing outwards of
        the polygon from the vertex of index = idx.
        """
        before = self.vertices[(idx - 1) % len(self.vertices)]
        current = self.vertices[idx]
        after = self.vertices[(idx + 1) % len(self.vertices)]
        current_to_after = after - current
        before_to_after = after - before
        dir = FPos((-before_to_after.y, before_to_after.x))
        return dir if dir.dot(current_to_after) < 0 else dir.inv()

    def closest_vertex(self, p: FPos) -> int:
        """Returns the index of the vertex closest to p."""
        indexes = range(len(self.vertices))
        return min(indexes, key=lambda i: self.vertices[i].dist(p))

    def __hash__(self) -> int:
        return hash(self.vertices)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ConvexPolygonHitbox):
            return False
        return self.vertices == other.vertices


class CircleHitbox(BoundedShape):
    def __init__(self, center: FPos, radius: float) -> None:
        self._center, self._radius = center, radius

    @property
    def center(self) -> FPos:
        return self._center

    @property
    def radius(self) -> float:
        return self._radius

    def _calculate_bounding_rect(self) -> Rect:
        c, r = self.center, self.radius
        return Rect(int(c.x - r), int(c.y - r), 2 * int(r), 2 * int(r))

    def __hash__(self) -> int:
        return hash((self.center, self.radius))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CircleHitbox):
            return False
        return self.center == other.center and self.radius == other.radius


Hitbox: TypeAlias = ConvexPolygonHitbox | CircleHitbox


class Collider(BoundedShape):
    def __init__(self, hitboxes: frozenset[Hitbox]) -> None:
        self._hitboxes = hitboxes

    @property
    def hitboxes(self) -> frozenset[Hitbox]:
        return self._hitboxes

    def _calculate_bounding_rect(self) -> Rect:
        rects = [h.bounding_rect for h in self.hitboxes]
        left = min(r.left for r in rects)
        right = max(r.left + r.width for r in rects)
        top = min(r.top for r in rects)
        bottom = max(r.top + r.height for r in rects)
        return Rect(int(left), int(top), int(right - left), int(bottom - top))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Collider):
            return False
        return self.hitboxes == other.hitboxes

    def __hash__(self) -> int:
        return hash(self.hitboxes)


class Collidable(Protocol):
    def get_collider(self) -> Collider: ...

    @property
    def collider_offset(self) -> FPos: ...

    def __hash__(self) -> int: ...
