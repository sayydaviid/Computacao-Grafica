from __future__ import annotations

import math

from core.types import FloatPoint, Point


def point_in_polygon(point: FloatPoint, polygon: list[Point]) -> bool:
    """Teste par-ímpar, útil para validar a semente."""

    x, y = point
    inside = False
    n = len(polygon)
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        intersects = ((yi > y) != (yj > y)) and (
            x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-12) + xi
        )
        if intersects:
            inside = not inside
        j = i
    return inside


def scanline_fill(polygon: list[Point]) -> set[Point]:
    """
    Preenchimento por varredura.
    Para cada linha y inteira, calcula interseções com arestas e preenche pares.
    """

    if len(polygon) < 3:
        return set()

    filled: set[Point] = set()
    min_y = math.ceil(min(y for _, y in polygon))
    max_y = math.floor(max(y for _, y in polygon))

    for y in range(min_y, max_y + 1):
        scan_y = y + 0.5
        intersections: list[float] = []

        for i in range(len(polygon)):
            x1, y1 = polygon[i]
            x2, y2 = polygon[(i + 1) % len(polygon)]

            if y1 == y2:
                continue

            lower_y, upper_y = sorted((y1, y2))
            if lower_y <= scan_y < upper_y:
                x = x1 + (scan_y - y1) * (x2 - x1) / (y2 - y1)
                intersections.append(x)

        intersections.sort()
        for i in range(0, len(intersections) - 1, 2):
            x_start = math.ceil(intersections[i])
            x_end = math.floor(intersections[i + 1])
            for x in range(x_start, x_end + 1):
                if point_in_polygon((x + 0.5, y + 0.5), polygon):
                    filled.add((x, y))

    return filled
