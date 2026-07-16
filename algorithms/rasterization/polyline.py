from __future__ import annotations

from core.types import Point
from algorithms.rasterization.bresenham import bresenham_line


def rasterize_polyline(points: list[Point], closed: bool = False) -> set[Point]:
    """Liga pontos consecutivos com Bresenham."""

    output: set[Point] = set()
    if len(points) < 2:
        return output

    # Se fechado e tem pelo menos 3 pontos, adiciona o primeiro ponto ao final
    if closed and len(points) >= 3:
        points = points + [points[0]]

    pairs = list(zip(points, points[1:]))

    for p0, p1 in pairs:
        output.update(bresenham_line(p0[0], p0[1], p1[0], p1[1]))
    return output
