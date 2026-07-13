from __future__ import annotations

import tkinter as tk
from typing import Optional

from core.constants import CANVAS_SIZE, CELL, GRID_SIZE, MAX_COORD, MIN_COORD
from core.types import Point


class GridCanvas(tk.Canvas):
    """Canvas cartesiano responsável por conversões e desenho da grade."""

    MIN_COORD = MIN_COORD
    MAX_COORD = MAX_COORD
    GRID_SIZE = GRID_SIZE
    CELL = CELL
    CANVAS_SIZE = CANVAS_SIZE

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(
            master,
            width=self.CANVAS_SIZE,
            height=self.CANVAS_SIZE,
            background="#f8fafc",
            highlightthickness=1,
            highlightbackground="#64748b",
        )

    def grid_to_canvas(self, x: int, y: int) -> tuple[int, int, int, int]:
        """Converte uma célula da grade para o retângulo no canvas."""

        col = x - self.MIN_COORD
        row = self.MAX_COORD - y
        x1 = col * self.CELL
        y1 = row * self.CELL
        return x1, y1, x1 + self.CELL, y1 + self.CELL

    def canvas_to_grid(self, px: int, py: int) -> Optional[Point]:
        """Converte coordenadas de tela para coordenadas inteiras da grade."""

        if not (0 <= px < self.CANVAS_SIZE and 0 <= py < self.CANVAS_SIZE):
            return None
        col = px // self.CELL
        row = py // self.CELL
        x = self.MIN_COORD + col
        y = self.MAX_COORD - row
        return x, y

    def in_bounds(self, point: Point) -> bool:
        """Indica se um ponto pertence à grade visível."""

        x, y = point
        return self.MIN_COORD <= x <= self.MAX_COORD and self.MIN_COORD <= y <= self.MAX_COORD

    def draw_grid(
        self,
        result_pixels: set[Point],
        input_points: list[Point],
        clipping_rect: Optional[tuple[int, int, int, int]],
    ) -> None:
        """Redesenha grade, janela de recorte, resultado e entradas."""

        self.delete("all")

        for i in range(self.GRID_SIZE + 1):
            pos = i * self.CELL
            self.create_line(pos, 0, pos, self.CANVAS_SIZE, fill="#cbd5e1")
            self.create_line(0, pos, self.CANVAS_SIZE, pos, fill="#cbd5e1")

        # Eixos: limites das células que separam -1/0 e 0/-1.
        axis_x = (0 - self.MIN_COORD) * self.CELL
        axis_y = (self.MAX_COORD - 0 + 1) * self.CELL
        self.create_line(axis_x, 0, axis_x, self.CANVAS_SIZE, fill="#334155", width=2)
        self.create_line(0, axis_y, self.CANVAS_SIZE, axis_y, fill="#334155", width=2)

        # Rótulos esparsos.
        for value in (-10, -5, 0, 5, 10):
            x1, _, x2, _ = self.grid_to_canvas(value, self.MIN_COORD)
            self.create_text((x1 + x2) / 2, self.CANVAS_SIZE - 8, text=str(value), fill="#475569")
            _, y1, _, y2 = self.grid_to_canvas(self.MIN_COORD, value)
            self.create_text(12, (y1 + y2) / 2, text=str(value), fill="#475569")

        if clipping_rect is not None:
            xmin, ymin, xmax, ymax = clipping_rect
            x1, y_top, _, _ = self.grid_to_canvas(xmin, ymax)
            _, _, x2, y_bottom = self.grid_to_canvas(xmax, ymin)
            self.create_rectangle(
                x1, y_top, x2, y_bottom,
                outline="#7c3aed", width=3, dash=(6, 3)
            )

        for point in result_pixels:
            self.paint_cell(point, "#0ea5e9")

        for index, point in enumerate(input_points):
            self.paint_cell(point, "#f97316")
            x1, y1, x2, y2 = self.grid_to_canvas(*point)
            self.create_text(
                (x1 + x2) / 2,
                (y1 + y2) / 2,
                text=str(index + 1),
                fill="white",
                font=("Arial", 9, "bold"),
            )

    def paint_cell(self, point: Point, color: str) -> None:
        """Pinta uma célula da grade se ela estiver dentro dos limites."""

        x, y = point
        if not self.in_bounds(point):
            return
        x1, y1, x2, y2 = self.grid_to_canvas(x, y)
        self.create_rectangle(
            x1 + 2, y1 + 2, x2 - 2, y2 - 2,
            fill=color, outline=""
        )
