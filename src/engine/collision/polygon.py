from math import atan2, pi

from ..essentials import FPos


def polar_angle(p1: FPos, p2: FPos) -> float:
    """
    Returns the angle between the x-axis and the
    segument (p1, p2) in the interval [-pi, pi).
    If p1 = p2, returns 0.
    """
    if p1.y == p2.y:
        if p1.x >= p2.x:
            return 0
        return -pi
    return atan2(p1.y - p2.y, p1.x - p2.x)


def argument(v: FPos) -> float:
    """Returns the argument of v. If v == 0, returns 0."""
    return 0 if (v.x, v.y) == (0, 0) else atan2(v.y, v.x)


def orientation(p1: FPos, p2: FPos, p3: FPos) -> int:
    """
    Consider the line segments L12 = (p1, p2), L23 = (p2, p3).
    Returns:
    - (1) if L12 -> L23 follows a clockwise trajectory,
    - (-1) if L12 -> L23 follows an anti-clockwise trajectory,
    - (0) if L12 and L23 are multiples of each other.
    """
    d = (p3.y - p2.y) * (p2.x - p1.x) - (p2.y - p1.y) * (p3.x - p2.x)
    if d > 0:
        return 1
    elif d < 0:
        return -1
    return 0


def graham_scan(vertices: list[FPos]) -> list[FPos]:
    """
    Returns the convex hull of the input points, ordered
    anti-clockwise. The first point is that with least
    positive  argument; in case of a draw, the one with
    least norm.
    """
    v0 = min(vertices, key=lambda p: (max(argument(p), 0), p.norm()))
    vertex_list = list(vertices)
    vertex_list.sort(key=lambda v: (polar_angle(v0, v), v0.dist(v)))
    hull: list[FPos] = []
    for vertex in vertex_list:
        while len(hull) >= 2 and orientation(hull[-2], hull[-1], vertex) != 1:
            hull.pop()
        hull.append(vertex)
    return hull
