from __future__ import annotations

import math

from core.types import FloatPoint, Point


def rotate_about(
    points: list[Point], angle_deg: float, pivot: FloatPoint
) -> list[Point]:
    """Aplica rotação 2D em torno de um pivô."""

    px, py = pivot
    angle = math.radians(angle_deg)
    cos_a, sin_a = math.cos(angle), math.sin(angle)

    transformed: list[Point] = []
    for x, y in points:
        dx, dy = x - px, y - py
        xr = px + dx * cos_a - dy * sin_a
        yr = py + dx * sin_a + dy * cos_a
        transformed.append((round(xr), round(yr)))
    return transformed
