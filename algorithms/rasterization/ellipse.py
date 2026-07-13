from __future__ import annotations

from core.types import Point
from algorithms.rasterization.bresenham import bresenham_line


def midpoint_ellipse(cx: int, cy: int, rx: int, ry: int) -> set[Point]:
    """Elipse pelo algoritmo do ponto médio."""

    if rx < 0 or ry < 0:
        raise ValueError("Os raios devem ser não negativos.")
    if rx == 0:
        return set(bresenham_line(cx, cy - ry, cx, cy + ry))
    if ry == 0:
        return set(bresenham_line(cx - rx, cy, cx + rx, cy))

    points: set[Point] = set()

    def add_symmetric(x: int, y: int) -> None:
        points.update({
            (cx + x, cy + y), (cx - x, cy + y),
            (cx + x, cy - y), (cx - x, cy - y),
        })

    x, y = 0, ry
    rx2, ry2 = rx * rx, ry * ry
    dx = 2 * ry2 * x
    dy = 2 * rx2 * y

    p1 = ry2 - rx2 * ry + 0.25 * rx2
    while dx < dy:
        add_symmetric(x, y)
        x += 1
        dx += 2 * ry2
        if p1 < 0:
            p1 += dx + ry2
        else:
            y -= 1
            dy -= 2 * rx2
            p1 += dx - dy + ry2

    p2 = ry2 * (x + 0.5) ** 2 + rx2 * (y - 1) ** 2 - rx2 * ry2
    while y >= 0:
        add_symmetric(x, y)
        y -= 1
        dy -= 2 * rx2
        if p2 > 0:
            p2 += rx2 - dy
        else:
            x += 1
            dx += 2 * ry2
            p2 += dx - dy + rx2

    return points
