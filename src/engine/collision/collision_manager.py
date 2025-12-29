from abc import ABC, abstractmethod
from dataclasses import dataclass
from itertools import product as iterprod
from typing import Any, Callable, Literal

from ..essentials import FPos, Pos
from ..utils import insertion_sort
from .collider import CircleHitbox, Collidable, Collider, ConvexPolygonHitbox, Hitbox
from .collision_detection import collide


class _Border(ABC):
    def __init__(self, collidable: Collidable, is_initial: bool) -> None:
        super().__init__()
        self.is_initial = is_initial
        self.collidable = collidable

    @property
    @abstractmethod
    def value(self) -> int: ...


class _YInitialBorder(_Border):
    def __init__(self, collidable: Collidable) -> None:
        super().__init__(collidable, True)

    @property
    def value(self) -> int:
        return self.collidable.get_collider().bounding_rect.top


class _YFinalBorder(_Border):
    def __init__(self, collidable: Collidable) -> None:
        super().__init__(collidable, False)

    @property
    def value(self) -> int:
        return self.collidable.get_collider().bounding_rect.bottom


class _XInitialBorder(_Border):
    def __init__(self, collidable: Collidable) -> None:
        super().__init__(collidable, True)

    @property
    def value(self) -> int:
        return self.collidable.get_collider().bounding_rect.left


class _XFinalBorder(_Border):
    def __init__(self, collidable: Collidable) -> None:
        super().__init__(collidable, False)

    @property
    def value(self) -> int:
        return self.collidable.get_collider().bounding_rect.right


class PreCollision:
    def __init__(self, obj1: Collidable, obj2: Collidable) -> None:
        self.obj1, self.obj2 = obj1, obj2

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PreCollision):
            return False
        if (
            self.obj1 == other.obj1
            and self.obj1.get_collider() == other.obj1.get_collider()
            and self.obj2 == other.obj2
            and self.obj2.get_collider() == other.obj2.get_collider()
        ):
            return True
        if (
            self.obj1 == other.obj2
            and self.obj1.get_collider() == other.obj2.get_collider()
            and self.obj2 == other.obj1
            and self.obj2.get_collider() == other.obj1.get_collider()
        ):
            return True
        return False

    def __hash__(self) -> int:
        return hash((self.obj1.get_collider(), self.obj2.get_collider()))


class Collision(PreCollision):
    def __init__(self, obj1: Collidable, obj2: Collidable, mdv: FPos) -> None:
        super().__init__(obj1, obj2)
        # Minimum distance vector, i.e. least translation of
        # obj1 so that the collision doesn't happen anymore.
        self.mdv = mdv

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Collision):
            return False
        if not super().__eq__(other):
            return False
        if self.obj1 == other.obj1:
            return self.mdv == other.mdv
        return self.mdv == other.mdv.inv()


class CollisionManager:
    def __init__(self) -> None:
        self.objs_to_remove: set[Collidable] = set()
        self.active_objs: set[Collidable] = set()
        self.x_sorted: list[_Border] = []
        self.y_sorted: list[_Border] = []
        self._collisions: frozenset[Collision] = frozenset()

    def update(self) -> None:
        self.sort_on_x()
        self.sort_on_y()
        self._collisions = self._update_collisions()

    def sort_on_x(self) -> None:
        size: Callable[[Any], int] = lambda v: v.value
        insertion_sort(self.x_sorted, size=size)

    def sort_on_y(self) -> None:
        size: Callable[[Any], int] = lambda v: v.value
        insertion_sort(self.y_sorted, size=size)

    def add_collidables(self, objs: frozenset[Collidable]) -> None:
        for obj in objs:
            self.add_collidable(obj)

    def add_collidable(self, obj: Collidable) -> None:
        self.x_sorted.append(_XInitialBorder(obj))
        self.x_sorted.append(_XFinalBorder(obj))
        self.y_sorted.append(_YInitialBorder(obj))
        self.y_sorted.append(_YFinalBorder(obj))
        self.active_objs.add(obj)
        self.update()

    def remove_collidable(self, obj: Collidable) -> None:
        self.objs_to_remove.add(obj)
        self.active_objs.remove(obj)

    def _update_collisions(self) -> frozenset[Collision]:
        return self._narrow_phase(self._broad_phase())

    def _broad_phase(self) -> frozenset[PreCollision]:
        colliding_in_x = self._broad_phase_in_axis("x")
        colliding_in_y = self._broad_phase_in_axis("y")
        self.objs_to_remove = set()
        return colliding_in_x.intersection(colliding_in_y)

    def _broad_phase_in_axis(self, axis: Literal["x", "y"]) -> frozenset[PreCollision]:
        """Implements the sweep-and-prune algorithm for one axis."""
        borders = self.x_sorted if axis == "x" else self.y_sorted
        pre_collisions: set[PreCollision] = set()
        touching_objs: set[Collidable] = set()
        borders_to_remove: set[_Border] = set()
        for border in borders:
            obj1 = border.collidable
            if obj1 in self.objs_to_remove:
                borders_to_remove.add(border)
                continue
            if not border.is_initial:
                touching_objs.remove(obj1)
                continue
            for obj2 in touching_objs:
                pre_collisions.add(PreCollision(obj1, obj2))
            touching_objs.add(obj1)
        for border in borders_to_remove:
            borders.remove(border)
        return frozenset(pre_collisions)

    def _narrow_phase(
        self, pre_collisions: frozenset[PreCollision]
    ) -> frozenset[Collision]:
        collisions: set[Collision] = set()
        for pre_collision in pre_collisions:
            obj1, obj2 = pre_collision.obj1, pre_collision.obj2
            offset = obj1.collider_offset - obj2.collider_offset
            if mdv := collide(obj1.get_collider(), obj2.get_collider(), offset):
                collisions.add(Collision(obj1, obj2, mdv))
        return frozenset(collisions)
