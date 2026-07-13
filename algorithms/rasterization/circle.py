from __future__ import annotations

from core.types import Point


def midpoint_circle(cx: int, cy: int, radius: int) -> set[Point]:
    """Círculo pelo algoritmo do ponto médio, usando simetria de 8 octantes."""

    if radius < 0:
        raise ValueError("O raio deve ser não negativo.")

    points: set[Point] = set()
    x, y = 0, radius
    decision = 1 - radius

    def add_symmetric(px: int, py: int) -> None:
        candidates = (
            (cx + px, cy + py), (cx - px, cy + py),
            (cx + px, cy - py), (cx - px, cy - py),
            (cx + py, cy + px), (cx - py, cy + px),
            (cx + py, cy - px), (cx - py, cy - px),
        )
        points.update(candidates)

    while x <= y:
        add_symmetric(x, y)
        x += 1
        if decision < 0:
            decision += 2 * x + 1
        else:
            y -= 1
            decision += 2 * (x - y) + 1

    return points
