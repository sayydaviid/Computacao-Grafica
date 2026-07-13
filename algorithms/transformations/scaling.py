from __future__ import annotations

from core.types import FloatPoint, Point


def scale_about(
    points: list[Point], sx: float, sy: float, fixed: FloatPoint
) -> list[Point]:
    """Aplica escala 2D usando um ponto fixo."""

    fx, fy = fixed
    return [
        (round(fx + sx * (x - fx)), round(fy + sy * (y - fy)))
        for x, y in points
    ]
