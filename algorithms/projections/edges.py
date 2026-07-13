from __future__ import annotations

from core.types import FloatPoint, Point
from algorithms.rasterization.bresenham import bresenham_line


def rasterize_edges(
    projected: list[FloatPoint], edges: list[tuple[int, int]]
) -> set[Point]:
    """Rasteriza arestas projetadas usando Bresenham."""

    pixels: set[Point] = set()
    rounded = [(round(x), round(y)) for x, y in projected]
    for i, j in edges:
        p0, p1 = rounded[i], rounded[j]
        pixels.update(bresenham_line(p0[0], p0[1], p1[0], p1[1]))
    return pixels
