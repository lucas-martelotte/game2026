import numpy as np


def epa_algorithm(
    poly1: np.ndarray, poly2: np.ndarray, simplex: np.ndarray, min_delta: float = 0.001
) -> np.ndarray:
    """
    Calculates the minimum translation vector of the collision according
    to the EPA algorithm. It stops when the square norm of the distance
    from the newly added point to the current closest point to the origin
    is less than min-delta.
    """
    test_poly = simplex
    while True:
        edge_index, closest_point = closest_edge(test_poly)
        new_point = full_support(closest_point, poly1, poly2)
        if np.any(np.all(test_poly == new_point, axis=1)):
            return closest_point
            # return closest_point, simplex, test_poly
        test_poly = np.insert(test_poly, edge_index + 1, new_point, 0)


def closest_edge(poly: np.ndarray) -> tuple[int, np.ndarray]:
    """
    Returns the closest edge to the origin and the point inside the edge
    that realizes the minimum distance. The algorithm assumes the input
    polygon is convex, which implies the closes point is NOT a vertice,
    but rather in the interior of an edge.

    This algorithm assumes that the polygon edges are properly sorted.
    Returns a tuple (i, x) where i is the edge index and x is the
    closest point to the origin.
    """
    least_distance: float = 9999999
    closest: tuple[int, np.ndarray] | None = None
    n_vertices = len(poly)
    for i in range(n_vertices):
        p, q = poly[i], poly[(i + 1) % n_vertices]
        p_norm, q_norm = np.inner(p, p), np.inner(q, q)
        cross_term = -(p[0] * q[0] + p[1] * q[1])
        t = (q_norm + cross_term) / (p_norm + q_norm + 2 * cross_term)
        closest_point = t * p + (1 - t) * q
        distance = float(np.linalg.norm(closest_point))
        if distance < least_distance:
            least_distance = distance
            closest = (i, closest_point)
    assert closest is not None
    return closest


def gjk_algorithm(poly1: np.ndarray, poly2: np.ndarray) -> np.ndarray | None:
    """Assumes poly1 and poly2 are N x 2 arrays of points"""
    initial_point = full_support(np.array([0, 1]), poly1, poly2)
    simplex = [initial_point]
    direction = -initial_point
    while True:
        new_point = full_support(direction, poly1, poly2)
        if list(new_point) == [0, 0]:
            return epa_algorithm(poly1, poly2, np.array(simplex))
        if np.dot(new_point, direction) < 0:
            return None
        simplex, direction, collided = do_simplex(simplex, new_point)
        if collided:
            return epa_algorithm(poly1, poly2, np.array(simplex))


def do_simplex(
    simplex: list[np.ndarray], a: np.ndarray
) -> tuple[list[np.ndarray], np.ndarray, bool]:
    if len(simplex) == 1:
        b, ab, d = simplex[0], simplex[0] - a, -a
        if np.dot(ab, d) > 0:
            new_direction = np.array([-ab[1], ab[0]])
            if np.dot(new_direction, d) < 0:
                new_direction = -new_direction
            return [a, b], new_direction, False
        return [a], d, False
    elif len(simplex) == 2:
        b, c, d = simplex[0], simplex[1], -a
        ab, ac = b - a, c - a
        alpha = np.array([-ac[1], ac[0]])
        if np.dot(alpha, ab) > 0:
            alpha = -alpha
        beta = np.array([ab[1], -ab[0]])
        if np.dot(beta, ac) > 0:
            beta = -beta
        if np.dot(alpha, d) > 0:
            if np.dot(ac, d) > 0:
                return [a, c], alpha, False
            else:
                return [a], d, False
        if np.dot(beta, d) > 0:
            if np.dot(ab, d) > 0:
                return [a, b], beta, False
            else:
                return [a], d, False
        return [b, c, a], np.zeros(2), True
    else:
        raise Exception("Unexpected error!")


def full_support(
    direction: np.ndarray, poly1: np.ndarray, poly2: np.ndarray
) -> np.ndarray:
    return support(direction, poly1) - support(-direction, poly2)


def support(direction: np.ndarray, poly: np.ndarray) -> np.ndarray:
    max_index = np.argmax(poly @ direction)
    return poly[max_index]
