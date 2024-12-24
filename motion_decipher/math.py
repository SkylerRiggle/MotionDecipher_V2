from math import pi, sqrt, atan2


RAD_2_DEG: float = 180.0 / pi
DEG_2_RAD: float = pi / 180.0

def compute_distance(point_a: tuple[float, float], point_b: tuple[float, float]) -> float:
    return sqrt(
        (point_a[0] - point_b[0])**2.0 +
        (point_a[1] - point_b[1])**2.0
    )

def compute_angle_deg(point_from: tuple[float, float], point_to: tuple[float, float]) -> float:
    return (
        360.0 + atan2(
            point_to[1] - point_from[1],
            point_to[0] - point_from[0]
        ) * RAD_2_DEG
    ) % 360.0

def normalize_3d(points: list[tuple[float, float, float]]) -> list[tuple[float, float, float]]:
    x_min = float("inf")
    x_max = float("-inf")
    y_min = float("inf")
    y_max = float("-inf")
    z_min = float("inf")
    z_max = float("-inf")

    for x, y, z in points:
        x_min = min(x_min, x)
        x_max = max(x_max, x)
        y_min = min(y_min, y)
        y_max = max(y_max, y)
        z_min = min(z_min, z)
        z_max = max(z_max, z)

    return [(
        (x - x_min) / (x_max - x_min),
        (y - y_min) / (y_max - y_min),
        (z - z_min) / (z_max - z_min),
    ) for x, y, z in points]