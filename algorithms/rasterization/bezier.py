from __future__ import annotations

from core.types import Point
from algorithms.rasterization.polyline import rasterize_polyline


def bezier_quadratic(p0: Point, p1: Point, p2: Point, samples: int = 100) -> set[Point]:
    """Bézier grau 2; amostras consecutivas são rasterizadas com Bresenham."""

    curve: list[Point] = []
    for i in range(samples + 1):
        t = i / samples
        mt = 1.0 - t
        x = mt * mt * p0[0] + 2 * mt * t * p1[0] + t * t * p2[0]
        y = mt * mt * p0[1] + 2 * mt * t * p1[1] + t * t * p2[1]
        curve.append((round(x), round(y)))
    return rasterize_polyline(curve)


def bezier_cubic(
    p0: Point, p1: Point, p2: Point, p3: Point, samples: int = 140
) -> set[Point]:
    """Bézier grau 3; amostras consecutivas são rasterizadas com Bresenham."""

    curve: list[Point] = []
    for i in range(samples + 1):
        t = i / samples
        mt = 1.0 - t
        x = (
            mt ** 3 * p0[0]
            + 3 * mt * mt * t * p1[0]
            + 3 * mt * t * t * p2[0]
            + t ** 3 * p3[0]
        )
        y = (
            mt ** 3 * p0[1]
            + 3 * mt * mt * t * p1[1]
            + 3 * mt * t * t * p2[1]
            + t ** 3 * p3[1]
        )
        curve.append((round(x), round(y)))
    return rasterize_polyline(curve)
