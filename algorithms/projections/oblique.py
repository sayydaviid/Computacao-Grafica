from __future__ import annotations

import math

from core.types import FloatPoint, Point3D


def oblique_projection(
    vertices: list[Point3D], angle_deg: float = 45.0, scale: float = 0.5
) -> list[FloatPoint]:
    """Aplica projeção oblíqua com ângulo e fator informados."""

    angle = math.radians(angle_deg)
    return [
        (x + scale * z * math.cos(angle), y + scale * z * math.sin(angle))
        for x, y, z in vertices
    ]
