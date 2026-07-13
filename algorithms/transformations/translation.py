from __future__ import annotations

from core.types import Point


def translate(points: list[Point], tx: float, ty: float) -> list[Point]:
    """Aplica translação 2D a uma lista de pontos."""

    return [(round(x + tx), round(y + ty)) for x, y in points]
