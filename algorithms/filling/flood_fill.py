from __future__ import annotations

from collections import deque

from core.types import Point


def flood_fill(
    seed: Point,
    boundary: set[Point],
    min_coord: int = -10,
    max_coord: int = 10,
) -> set[Point]:
    """
    Preenchimento 4-conexo iterativo.
    A versão iterativa evita estouro da pilha de recursão.
    """

    if seed in boundary:
        return set()

    filled: set[Point] = set()
    queue: deque[Point] = deque([seed])

    while queue:
        x, y = queue.popleft()
        if (
            x < min_coord or x > max_coord
            or y < min_coord or y > max_coord
            or (x, y) in boundary
            or (x, y) in filled
        ):
            continue

        filled.add((x, y))
        queue.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))

    return filled
