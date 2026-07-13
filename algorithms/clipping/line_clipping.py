from __future__ import annotations

from typing import Optional

from core.types import FloatPoint, Point

INSIDE, LEFT, RIGHT, BOTTOM, TOP = 0, 1, 2, 4, 8


def _region_code(x: float, y: float, xmin: float, ymin: float, xmax: float, ymax: float) -> int:
    """Calcula o código de região Cohen-Sutherland para um ponto."""

    code = INSIDE
    if x < xmin:
        code |= LEFT
    elif x > xmax:
        code |= RIGHT
    if y < ymin:
        code |= BOTTOM
    elif y > ymax:
        code |= TOP
    return code


def cohen_sutherland_clip(
    p0: Point, p1: Point, rect: tuple[int, int, int, int]
) -> Optional[tuple[FloatPoint, FloatPoint]]:
    """Recorte de linha Cohen-Sutherland."""

    xmin, ymin, xmax, ymax = rect
    x0, y0 = map(float, p0)
    x1, y1 = map(float, p1)

    while True:
        code0 = _region_code(x0, y0, xmin, ymin, xmax, ymax)
        code1 = _region_code(x1, y1, xmin, ymin, xmax, ymax)

        if not (code0 | code1):
            return (x0, y0), (x1, y1)
        if code0 & code1:
            return None

        code_out = code0 or code1

        if code_out & TOP:
            if y1 == y0:
                return None
            x = x0 + (x1 - x0) * (ymax - y0) / (y1 - y0)
            y = ymax
        elif code_out & BOTTOM:
            if y1 == y0:
                return None
            x = x0 + (x1 - x0) * (ymin - y0) / (y1 - y0)
            y = ymin
        elif code_out & RIGHT:
            if x1 == x0:
                return None
            y = y0 + (y1 - y0) * (xmax - x0) / (x1 - x0)
            x = xmax
        else:
            if x1 == x0:
                return None
            y = y0 + (y1 - y0) * (xmin - x0) / (x1 - x0)
            x = xmin

        if code_out == code0:
            x0, y0 = x, y
        else:
            x1, y1 = x, y
