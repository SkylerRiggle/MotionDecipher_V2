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