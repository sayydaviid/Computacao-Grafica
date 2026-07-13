from __future__ import annotations

from core.types import Point3D

MIN_COORD = -10
MAX_COORD = 10
GRID_SIZE = 21
CELL = 30
CANVAS_SIZE = GRID_SIZE * CELL

CUBE_VERTICES: list[Point3D] = [
    (-4, -4, -4), (4, -4, -4), (4, 4, -4), (-4, 4, -4),
    (-4, -4, 4), (4, -4, 4), (4, 4, 4), (-4, 4, 4),
]

CUBE_EDGES: list[tuple[int, int]] = [
    (0, 1), (1, 2), (2, 3), (3, 0),
    (4, 5), (5, 6), (6, 7), (7, 4),
    (0, 4), (1, 5), (2, 6), (3, 7),
]
