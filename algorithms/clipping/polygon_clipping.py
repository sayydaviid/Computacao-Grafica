from __future__ import annotations

from typing import Callable

from core.types import FloatPoint


def sutherland_hodgman_clip(
    polygon: list[FloatPoint], rect: tuple[int, int, int, int]
) -> list[FloatPoint]:
    """Recorte de polígono contra janela retangular."""

    xmin, ymin, xmax, ymax = rect

    def clip_edge(
        vertices: list[FloatPoint],
        inside: Callable[[FloatPoint], bool],
        intersect: Callable[[FloatPoint, FloatPoint], FloatPoint],
    ) -> list[FloatPoint]:
        if not vertices:
            return []

        output: list[FloatPoint] = []
        previous = vertices[-1]

        for current in vertices:
            curr_inside = inside(current)
            prev_inside = inside(previous)

            if curr_inside:
                if not prev_inside:
                    output.append(intersect(previous, current))
                output.append(current)
            elif prev_inside:
                output.append(intersect(previous, current))

            previous = current

        return output

    def vertical_intersection(a: FloatPoint, b: FloatPoint, x_edge: float) -> FloatPoint:
        x1, y1 = a
        x2, y2 = b
        if x2 == x1:
            return x_edge, y1
        t = (x_edge - x1) / (x2 - x1)
        return x_edge, y1 + t * (y2 - y1)

    def horizontal_intersection(a: FloatPoint, b: FloatPoint, y_edge: float) -> FloatPoint:
        x1, y1 = a
        x2, y2 = b
        if y2 == y1:
            return x1, y_edge
        t = (y_edge - y1) / (y2 - y1)
        return x1 + t * (x2 - x1), y_edge

    result = polygon[:]
    result = clip_edge(result, lambda p: p[0] >= xmin,
                       lambda a, b: vertical_intersection(a, b, xmin))
    result = clip_edge(result, lambda p: p[0] <= xmax,
                       lambda a, b: vertical_intersection(a, b, xmax))
    result = clip_edge(result, lambda p: p[1] >= ymin,
                       lambda a, b: horizontal_intersection(a, b, ymin))
    result = clip_edge(result, lambda p: p[1] <= ymax,
                       lambda a, b: horizontal_intersection(a, b, ymax))
    return result
