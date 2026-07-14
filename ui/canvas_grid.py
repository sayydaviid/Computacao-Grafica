from __future__ import annotations

import tkinter as tk
from typing import Optional

from core.constants import CANVAS_SIZE, GRID_SIZE, MAX_COORD, MIN_COORD
from core.types import Point


class GridCanvas(tk.Canvas):
    """Canvas cartesiano responsável por conversões e desenho da grade."""

    MIN_COORD = MIN_COORD
    MAX_COORD = MAX_COORD
    GRID_SIZE = GRID_SIZE
    MIN_CANVAS_SIZE = GRID_SIZE * 12

    def __init__(self, master: tk.Misc) -> None:
        self.canvas_size = CANVAS_SIZE
        self.cell_size = self.canvas_size / self.GRID_SIZE
        super().__init__(
            master,
            width=self.canvas_size,
            height=self.canvas_size,
            background="#f8fafc",
            highlightthickness=1,
            highlightbackground="#64748b",
        )

    def set_canvas_size(self, canvas_size: int) -> bool:
        """Atualiza o tamanho visual quadrado da grade."""

        size = max(self.MIN_CANVAS_SIZE, int(canvas_size))
        if size == self.canvas_size:
            return False

        self.canvas_size = size
        self.cell_size = self.canvas_size / self.GRID_SIZE
        self.configure(width=self.canvas_size, height=self.canvas_size)
        return True

    def grid_to_canvas(self, x: int, y: int) -> tuple[float, float, float, float]:
        """Converte uma célula da grade para o retângulo no canvas."""

        col = x - self.MIN_COORD
        row = self.MAX_COORD - y
        x1 = col * self.cell_size
        y1 = row * self.cell_size
        return x1, y1, x1 + self.cell_size, y1 + self.cell_size

    def canvas_to_grid(self, px: int, py: int) -> Optional[Point]:
        """Converte coordenadas de tela para coordenadas inteiras da grade."""

        if not (0 <= px < self.canvas_size and 0 <= py < self.canvas_size):
            return None

        col = int(px / self.cell_size)
        row = int(py / self.cell_size)
        col = min(max(col, 0), self.GRID_SIZE - 1)
        row = min(max(row, 0), self.GRID_SIZE - 1)
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
            pos = i * self.cell_size
            self.create_line(pos, 0, pos, self.canvas_size, fill="#cbd5e1")
            self.create_line(0, pos, self.canvas_size, pos, fill="#cbd5e1")

        # Eixos: limites das células que separam -1/0 e 0/-1.
        axis_x = (0 - self.MIN_COORD) * self.cell_size
        axis_y = (self.MAX_COORD - 0 + 1) * self.cell_size
        self.create_line(axis_x, 0, axis_x, self.canvas_size, fill="#334155", width=2)
        self.create_line(0, axis_y, self.canvas_size, axis_y, fill="#334155", width=2)

        # Rótulos esparsos.
        for value in (-10, -5, 0, 5, 10):
            x1, _, x2, _ = self.grid_to_canvas(value, self.MIN_COORD)
            self.create_text((x1 + x2) / 2, self.canvas_size - 8, text=str(value), fill="#475569")
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
        inset = max(1.0, min(3.0, self.cell_size * 0.08))
        self.create_rectangle(
            x1 + inset, y1 + inset, x2 - inset, y2 - inset,
            fill=color, outline=""
        )
