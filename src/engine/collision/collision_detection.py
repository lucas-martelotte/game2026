from itertools import product as iterprod

from numpy import array

from ..essentials import FPos, Pos, Rect
from .collider import CircleHitbox, Collider, ConvexPolygonHitbox, Hitbox
from .gjk import gjk_algorithm


def collide(
    c1: Collider, c2: Collider, offset: FPos, number_of_trials: int = 2
) -> FPos | None:
    """
    Let C1 = c1 translated by offset, C2 = c2. Returns None if
    C1 and C2 do not collide, otherwise returns a translation
    'mdv' of C1 which resolves the collision. If c1 and c2
    both have a single hitbox, mdv is guaranteed to be the
    minimum distance vector.

    The parameter number_of_trials indicates the maximum
    number of collision checks before falling back to the
    AABB collision between the bounding rects of C1, C2.
    """
    total_mdv, current_trial = FPos((0, 0)), 0
    while current_trial < number_of_trials:
        mdvs: list[FPos | None] = [
            collide_hitboxes(h1, h2, offset + total_mdv)
            for h1, h2 in iterprod(c1.hitboxes, c2.hitboxes)
        ]
        mdvs_filtered = [mdv for mdv in mdvs if mdv is not None]
        mdv_increment = sum(mdvs_filtered, FPos((0, 0)))
        if mdv_increment == FPos((0, 0)):  # No collision
            return total_mdv
        current_trial += 1
        total_mdv += mdv_increment
    # At this point, we were unable to resolve the collision
    # We will then just run the algorithm for the bounding rect
    return aabb(c1.bounding_rect, c2.bounding_rect)


def aabb(r1: Rect, r2: Rect) -> Pos | None:
    """
    Checks for intersections using the AABB algorithm.
    Returns None if there is no collision, otherwise
    returns the minimum translation of self which
    resolves the collision.
    """

    def check(r1: Rect, r2: Rect) -> bool:
        return (
            r1.left <= r2.right
            and r1.right >= r2.left
            and r1.top <= r2.bottom
            and r1.bottom >= r2.top
        )

    collide = check(r1, r2) or check(r2, r1)
    if not collide:
        return None
    candidates_for_mdv: list[tuple[Pos, int]] = []
    size = max(r2.bottom - r1.top, 0)
    candidates_for_mdv.append((Pos((0, size)), abs(size)))
    size = max(r2.top - r1.bottom, 0)
    candidates_for_mdv.append((Pos((0, size)), abs(size)))
    size = max(r2.right - r1.left, 0)
    candidates_for_mdv.append((Pos((size, 0)), abs(size)))
    size = max(r2.left - r1.right, 0)
    candidates_for_mdv.append((Pos((size, 0)), abs(size)))
    return sorted(candidates_for_mdv, key=lambda x: x[1])[0][0]


def collide_hitboxes(h1: Hitbox, h2: Hitbox, offset: FPos) -> FPos | None:
    if isinstance(h1, CircleHitbox):
        if isinstance(h2, CircleHitbox):
            return circle_circle_collision(h1, h2, offset)
        return circle_convex_polygon_collision(h1, h2, offset)
    if isinstance(h2, CircleHitbox):
        return convex_polygon_circle_collision(h1, h2, offset)
    return convex_polygon_convex_polygon_collision(h1, h2, offset)


def circle_convex_polygon_collision(
    h1: CircleHitbox, h2: ConvexPolygonHitbox, offset: FPos
) -> FPos | None:
    center_moved = h1.center + offset
    closest_idx = h2.closest_vertex(center_moved)
    outward_dir = h2.get_outwards_direction(closest_idx)
    dist = h2.vertices[closest_idx].dist(h1.center)
    return outward_dir * dist


def convex_polygon_circle_collision(
    h1: ConvexPolygonHitbox, h2: CircleHitbox, offset: FPos
) -> FPos | None:
    mdv = circle_convex_polygon_collision(h2, h1, offset.inv())
    return None if mdv is None else mdv.inv()


def circle_circle_collision(
    h1: CircleHitbox,
    h2: CircleHitbox,
    offset: FPos,
    minimum_allowed_distance: float = 0.01,
) -> FPos | None:
    diff = h1.center + offset - h2.center
    center_dist = diff.norm()
    if center_dist <= minimum_allowed_distance:  # centers are equal
        return FPos((max(h1.radius, h2.radius), 0))
    mdv_size = h1.radius + h2.radius - center_dist
    if mdv_size <= 0:
        return None  # No collision
    return diff * (mdv_size / center_dist)


def convex_polygon_convex_polygon_collision(
    h1: ConvexPolygonHitbox, h2: ConvexPolygonHitbox, offset: FPos
) -> FPos | None:
    offset_array = array([[offset.to_tuple()] * len(h1.vertices)])
    mpv_array = gjk_algorithm(h1.array + offset_array, h2.array)
    return None if mpv_array is None else FPos(tuple(mpv_array))


# =================== #
# == GJK ALGORITHM == #
# =================== #
