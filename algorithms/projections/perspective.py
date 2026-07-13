from __future__ import annotations

from core.types import FloatPoint, Point3D


def perspective_projection(
    vertices: list[Point3D], distance: float = 14.0
) -> list[FloatPoint]:
    """Aplica projeção perspectiva a vértices 3D."""

    projected: list[FloatPoint] = []
    for x, y, z in vertices:
        denominator = distance + z
        if abs(denominator) < 1e-9:
            denominator = 1e-9
        factor = distance / denominator
        projected.append((x * factor, y * factor))
    return projected
