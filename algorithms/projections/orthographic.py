from __future__ import annotations

from core.types import FloatPoint, Point3D


def orthographic_projection(vertices: list[Point3D]) -> list[FloatPoint]:
    """Projeta vértices 3D no plano XY."""

    return [(x, y) for x, y, _ in vertices]
