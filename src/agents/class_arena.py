import numpy as np
from shapely.geometry import Point, Polygon
from shapely.prepared import prep
from shapely.vectorized import contains as vec_contains


class ShapeSampler:
    def __init__(self, boundary_points, ordered=True, fix_invalid=True):
        """
        boundary_points : (N, 2) array-like of surface points.
        ordered         : True if points are already sequential along the boundary.
                          False -> will attempt nearest-neighbour ordering.
        """
        pts = np.asarray(boundary_points, dtype=float)

        if not ordered:
            pts = self._order_points_nn(pts)

        poly = Polygon(pts)
        if fix_invalid and not poly.is_valid:
            poly = poly.buffer(0)  # repairs minor self-intersections

        self.polygon = poly
        self._prepared = prep(self.polygon)
        self.bounds = self.polygon.bounds  # (minx, miny, maxx, maxy)

    # ---------- boundary ordering (fallback for messy point clouds) ----------
    @staticmethod
    def _order_points_nn(pts):
        """Greedy nearest-neighbour chain. Works OK for simple concave shapes,
        but for noisy/complex clouds prefer an alpha-shape (see below)."""
        pts = pts.copy()
        n = len(pts)
        visited = np.zeros(n, dtype=bool)
        order = [0]
        visited[0] = True
        for _ in range(n - 1):
            last = pts[order[-1]]
            d = np.linalg.norm(pts - last, axis=1)
            d[visited] = np.inf
            nxt = int(np.argmin(d))
            order.append(nxt)
            visited[nxt] = True
        return pts[order]

    # ---------------------------- bounding box --------------------------------
    def bounding_box(self):
        """Returns (minx, miny, maxx, maxy)."""
        return self.bounds

    # ---------------------------- point-in-shape -------------------------------
    def is_inside(self, point, strict=True):
        """
        point  : (x, y)
        strict : True  -> boundary points count as OUTSIDE (i.e. must be strictly interior)
                 False -> boundary points count as inside too
        """
        p = Point(point)
        if strict:
            return self._prepared.contains(p)
        return self._prepared.contains(p) or self.polygon.boundary.distance(p) < 1e-9

    def is_inside_batch(self, points):
        """Vectorized check for many points at once. Returns boolean array."""
        points = np.asarray(points, dtype=float)
        return vec_contains(self.polygon, points[:, 0], points[:, 1])

    # ---------------------------- sampling --------------------------------
    def generate_points_inside(self, n, seed=None, batch_size=None):
        """Rejection-sample n points strictly inside the shape."""
        rng = np.random.default_rng(seed)
        minx, miny, maxx, maxy = self.bounds
        if batch_size is None:
            batch_size = max(4 * n, 1000)

        pts = np.empty((0, 2))
        while len(pts) < n:
            x = rng.uniform(minx, maxx, batch_size)
            y = rng.uniform(miny, maxy, batch_size)
            mask = vec_contains(self.polygon, x, y)
            new_pts = np.column_stack([x[mask], y[mask]])
            pts = np.vstack([pts, new_pts])
        return pts[:n]


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    # Example: an ordered set of boundary points (e.g., a star/concave polygon)
    boundary = np.array(
        [[0, 0], [2, 0], [2, 1], [1, 1], [1, 2], [2, 2], [2, 3], [0, 3], [0, 0]]
    )

    shape = ShapeSampler(boundary, ordered=True)

    print("Bounding box:", shape.bounding_box())

    pts_inside = shape.generate_points_inside(200, seed=42)

    print("Point (0.5, 0.5) inside?", shape.is_inside((0.5, 0.5)))
    print(
        "Point (1.5, 1.5) inside?", shape.is_inside((1.5, 1.5))
    )  # in the "notch" -> False
    print(
        "Point (1.5, 1.0) inside?", shape.is_inside((1.5, 1.0))
    )  # in the "notch" -> False
    # Visualize
    fig, ax = plt.subplots()
    x, y = shape.polygon.exterior.xy
    ax.plot(x, y, "k-")
    ax.scatter(pts_inside[:, 0], pts_inside[:, 1], s=5, c="r")
    ax.set_aspect("equal")
    plt.show()
