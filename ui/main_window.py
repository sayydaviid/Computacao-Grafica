from __future__ import annotations

import math
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable, Iterable, Optional

from algorithms.clipping.line_clipping import cohen_sutherland_clip
from algorithms.clipping.polygon_clipping import sutherland_hodgman_clip
from algorithms.filling.flood_fill import flood_fill
from algorithms.filling.scanline import point_in_polygon, scanline_fill
from algorithms.projections.edges import rasterize_edges
from algorithms.projections.oblique import oblique_projection
from algorithms.projections.orthographic import orthographic_projection
from algorithms.projections.perspective import perspective_projection
from algorithms.rasterization.bezier import bezier_cubic, bezier_quadratic
from algorithms.rasterization.bresenham import bresenham_line
from algorithms.rasterization.circle import midpoint_circle
from algorithms.rasterization.ellipse import midpoint_ellipse
from algorithms.rasterization.polyline import rasterize_polyline
from algorithms.transformations.rotation import rotate_about
from algorithms.transformations.scaling import scale_about
from algorithms.transformations.translation import translate
from core.constants import CUBE_EDGES, CUBE_VERTICES, GRID_SIZE, MAX_COORD, MIN_COORD
from core.types import Point
from models.algorithm_spec import ALGORITHMS
from ui.canvas_grid import GridCanvas
from ui.control_panel import ControlPanel
from ui.three_d_view import ThreeDViewer


class RasterApp(tk.Tk):
    """Janela principal que coordena estado, entrada e execução dos algoritmos."""

    MIN_COORD = MIN_COORD
    MAX_COORD = MAX_COORD
    GRID_SIZE = GRID_SIZE

    def __init__(self) -> None:
        super().__init__()
        self.title("Rasterizador CG — Algoritmos do Trabalho Prático")
        self.geometry("1180x760")
        self.minsize(900, 600)

        self.algorithm_var = tk.StringVar(value="Bresenham")
        self.status_var = tk.StringVar()
        self.coords_var = tk.StringVar(value="Coordenada: —")
        self.input_points: list[Point] = []
        self.result_pixels: set[Point] = set()
        self.boundary_pixels: set[Point] = set()
        self.clipping_rect: Optional[tuple[int, int, int, int]] = None
        self._resize_job: str | None = None

        self._build_style()
        self._build_layout()
        self._on_algorithm_changed()
        self.draw_grid()
        self.after_idle(self._apply_responsive_layout)

    def _build_style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Title.TLabel", font=("Arial", 16, "bold"))
        style.configure("Section.TLabel", font=("Arial", 11, "bold"))
        style.configure("Primary.TButton", font=("Arial", 10, "bold"))

    def _build_layout(self) -> None:
        main = ttk.Frame(self, padding=12)
        main.pack(fill=tk.BOTH, expand=True)
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=0, minsize=ControlPanel.PANEL_WIDTH)
        main.rowconfigure(0, weight=1)

        left = ttk.Frame(main)
        left.grid(row=0, column=0, sticky="nsew")
        left.columnconfigure(0, weight=1)
        left.rowconfigure(1, weight=1)

        self.control_panel = ControlPanel(
            main,
            self.algorithm_var,
            self.status_var,
            self._on_algorithm_changed,
            self.execute_algorithm,
            self.undo_last_point,
            self.clear_all,
            self.open_3d_view,
        )
        self.control_panel.grid(row=0, column=1, sticky="nsew", padx=(14, 0))
        self.control_panel.grid_propagate(False)


        self.canvas_area = ttk.Frame(left)
        self.canvas_area.grid(row=1, column=0, sticky="nsew", pady=(8, 4))
        self.canvas_area.columnconfigure(0, weight=1)
        self.canvas_area.rowconfigure(0, weight=1)
        self.canvas_area.bind("<Configure>", self._on_resize)

        self.canvas = GridCanvas(self.canvas_area)
        self.canvas.grid(row=0, column=0)
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<Motion>", self._on_canvas_motion)

        ttk.Label(left, textvariable=self.coords_var).grid(row=2, column=0, sticky="w")
        self.legend_label = ttk.Label(
            left,
            text="Azul = resultado | Laranja = entradas | Roxo = janela de recorte | Cinza = grade",
            justify=tk.LEFT,
        )
        self.legend_label.grid(row=3, column=0, sticky="ew", pady=(2, 0))

    def _on_resize(self, event: tk.Event) -> None:
        if event.widget is not self.canvas_area:
            return

        if self._resize_job is not None:
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(100, self._apply_responsive_layout)

    def _apply_responsive_layout(self) -> None:
        self._resize_job = None
        available_width = self.canvas_area.winfo_width()
        available_height = self.canvas_area.winfo_height()
        if available_width <= 1 or available_height <= 1:
            return

        self.legend_label.configure(wraplength=max(260, available_width))
        canvas_size = min(available_width, available_height) - 2
        if self.canvas.set_canvas_size(canvas_size):
            self.draw_grid()

    def draw_grid(self) -> None:
        """Solicita ao canvas o redesenho do estado atual."""

        self.canvas.draw_grid(
            self.result_pixels,
            self.input_points,
            self.clipping_rect,
        )

    def _on_canvas_motion(self, event: tk.Event) -> None:
        point = self.canvas.canvas_to_grid(event.x, event.y)
        self.coords_var.set(f"Coordenada: {point}" if point else "Coordenada: —")

    def _on_canvas_click(self, event: tk.Event) -> None:
        point = self.canvas.canvas_to_grid(event.x, event.y)
        if point is None:
            return

        spec = ALGORITHMS[self.algorithm_var.get()]
        if spec.clicks == 0:
            messagebox.showinfo("Entrada", "Este algoritmo não exige cliques na grade.")
            return

        if spec.clicks is not None and len(self.input_points) >= spec.clicks:
            messagebox.showinfo(
                "Limite de pontos",
                "Todos os pontos necessários já foram selecionados. "
                "Use Executar ou Limpar tudo."
            )
            return

        self.input_points.append(point)
        self.result_pixels.clear()
        self._refresh_points_list()
        self.draw_grid()
        self._update_action_buttons()

        if spec.auto_execute and spec.clicks is not None and len(self.input_points) == spec.clicks:
            self.execute_algorithm()

    def _on_algorithm_changed(self) -> None:
        algorithm = self.algorithm_var.get()
        if algorithm not in ALGORITHMS:
            return

        self.clear_all(keep_algorithm=True)
        spec = ALGORITHMS[algorithm]
        self.status_var.set(spec.instruction)
        self.control_panel.update_for_algorithm(spec)
        self._update_action_buttons()

    def undo_last_point(self) -> None:
        if self.input_points:
            self.input_points.pop()
            self.result_pixels.clear()
            self._refresh_points_list()
            self.draw_grid()
            self._update_action_buttons()

    def clear_all(self, keep_algorithm: bool = True) -> None:
        self.input_points.clear()
        self.result_pixels.clear()
        self.boundary_pixels.clear()
        self.clipping_rect = None
        if hasattr(self, "control_panel"):
            self._refresh_points_list()
        if hasattr(self, "canvas"):
            self.draw_grid()
        self._update_action_buttons()

    def _has_viewable_state(self) -> bool:
        return bool(
            self.input_points
            or self.result_pixels
            or self.boundary_pixels
            or self.clipping_rect
        )

    def _update_action_buttons(self) -> None:
        if not hasattr(self, "control_panel"):
            return

        self.control_panel.set_view_3d_enabled(self._has_viewable_state())

    def open_3d_view(self) -> None:
        if not self._has_viewable_state():
            return

        viewer = ThreeDViewer(
            parent=self,
            input_points=self.input_points,
            result_pixels=self.result_pixels,
            clipping_rect=self.clipping_rect,
        )
        viewer.show()

    def _refresh_points_list(self) -> None:
        self.control_panel.refresh_points_list(self.input_points)

    def in_bounds(self, point: Point) -> bool:
        return self.canvas.in_bounds(point)

    def _value(self, key: str, cast: Callable = float):
        return self.control_panel.value(key, cast)

    def _rect(self) -> tuple[int, int, int, int]:
        xmin = self._value("xmin", int)
        ymin = self._value("ymin", int)
        xmax = self._value("xmax", int)
        ymax = self._value("ymax", int)

        if xmin >= xmax or ymin >= ymax:
            raise ValueError("A janela precisa satisfazer xmin < xmax e ymin < ymax.")
        if not (
            self.MIN_COORD <= xmin <= self.MAX_COORD
            and self.MIN_COORD <= xmax <= self.MAX_COORD
            and self.MIN_COORD <= ymin <= self.MAX_COORD
            and self.MIN_COORD <= ymax <= self.MAX_COORD
        ):
            raise ValueError("A janela deve ficar dentro da grade de -10 a 10.")

        return xmin, ymin, xmax, ymax

    def _require_points(self, count: int) -> None:
        if len(self.input_points) != count:
            raise ValueError(f"Este algoritmo exige exatamente {count} pontos.")

    def _require_polygon(self, minimum: int = 3) -> None:
        if len(self.input_points) < minimum:
            raise ValueError(f"Selecione pelo menos {minimum} vértices.")

    def _filter_bounds(self, points: Iterable[Point]) -> set[Point]:
        return {p for p in points if self.in_bounds(p)}

    def execute_algorithm(self) -> None:
        """Executa o algoritmo selecionado com os pontos e parâmetros atuais."""

        algorithm = self.algorithm_var.get()
        self.result_pixels.clear()
        self.boundary_pixels.clear()
        self.clipping_rect = None

        try:
            if algorithm == "Bresenham":
                self._require_points(2)
                p0, p1 = self.input_points
                result = bresenham_line(*p0, *p1)

            elif algorithm == "Círculo":
                self._require_points(2)
                center, edge = self.input_points
                radius = round(math.dist(center, edge))
                result = midpoint_circle(center[0], center[1], radius)

            elif algorithm == "Elipse":
                self._require_points(3)
                center, horizontal, vertical = self.input_points
                rx = abs(horizontal[0] - center[0])
                ry = abs(vertical[1] - center[1])
                if rx == 0 or ry == 0:
                    raise ValueError(
                        "O ponto horizontal deve alterar X e o vertical deve alterar Y."
                    )
                result = midpoint_ellipse(center[0], center[1], rx, ry)

            elif algorithm == "Bézier grau 2":
                self._require_points(3)
                result = bezier_quadratic(*self.input_points)

            elif algorithm == "Bézier grau 3":
                self._require_points(4)
                result = bezier_cubic(*self.input_points)

            elif algorithm == "Polilinha":
                self._require_polygon(4)
                result = rasterize_polyline(self.input_points, closed=False)

            elif algorithm == "Preenchimento recursivo":
                self._require_polygon(3)
                boundary = rasterize_polyline(self.input_points, closed=True)
                seed = (self._value("seed_x", int), self._value("seed_y", int))
                if not point_in_polygon((seed[0] + 0.5, seed[1] + 0.5), self.input_points):
                    raise ValueError("A semente deve estar no interior do polígono.")
                self.boundary_pixels = boundary
                result = boundary | flood_fill(
                    seed, boundary, self.MIN_COORD, self.MAX_COORD
                )

            elif algorithm == "Preenchimento por varredura":
                self._require_polygon(3)
                boundary = rasterize_polyline(self.input_points, closed=True)
                self.boundary_pixels = boundary
                result = boundary | scanline_fill(self.input_points)

            elif algorithm == "Recorte de linha":
                self._require_points(2)
                rect = self._rect()
                self.clipping_rect = rect
                clipped = cohen_sutherland_clip(
                    self.input_points[0], self.input_points[1], rect
                )
                if clipped is None:
                    result = set()
                    messagebox.showinfo(
                        "Recorte",
                        "A linha está totalmente fora da janela de recorte."
                    )
                else:
                    p0, p1 = clipped
                    rp0 = (round(p0[0]), round(p0[1]))
                    rp1 = (round(p1[0]), round(p1[1]))
                    result = bresenham_line(*rp0, *rp1)

            elif algorithm == "Recorte de polígono":
                self._require_polygon(3)
                rect = self._rect()
                self.clipping_rect = rect
                clipped = sutherland_hodgman_clip(
                    [(float(x), float(y)) for x, y in self.input_points],
                    rect,
                )
                if len(clipped) < 3:
                    result = set()
                    messagebox.showinfo(
                        "Recorte",
                        "O polígono ficou totalmente fora da janela."
                    )
                else:
                    rounded = [(round(x), round(y)) for x, y in clipped]
                    result = rasterize_polyline(rounded, closed=True)

            elif algorithm == "Translação":
                self._require_polygon(3)
                transformed = translate(
                    self.input_points,
                    self._value("tx"),
                    self._value("ty"),
                )
                result = rasterize_polyline(transformed, closed=True)

            elif algorithm == "Escala":
                self._require_polygon(3)
                transformed = scale_about(
                    self.input_points,
                    self._value("sx"),
                    self._value("sy"),
                    (self._value("fixed_x"), self._value("fixed_y")),
                )
                result = rasterize_polyline(transformed, closed=True)

            elif algorithm == "Rotação":
                self._require_polygon(3)
                transformed = rotate_about(
                    self.input_points,
                    self._value("angle"),
                    (self._value("pivot_x"), self._value("pivot_y")),
                )
                result = rasterize_polyline(transformed, closed=True)

            elif algorithm == "Projeção ortográfica":
                projected = orthographic_projection(CUBE_VERTICES)
                result = rasterize_edges(projected, CUBE_EDGES)

            elif algorithm == "Projeção oblíqua":
                projected = oblique_projection(
                    CUBE_VERTICES,
                    self._value("angle"),
                    self._value("oblique_scale"),
                )
                result = rasterize_edges(projected, CUBE_EDGES)

            elif algorithm == "Projeção perspectiva":
                distance = self._value("camera_distance")
                if distance <= 4:
                    raise ValueError(
                        "Use distância da câmera maior que 4 para evitar singularidade."
                    )
                projected = perspective_projection(CUBE_VERTICES, distance)
                result = rasterize_edges(projected, CUBE_EDGES)

            else:
                raise ValueError("Algoritmo desconhecido.")

            self.result_pixels = self._filter_bounds(result)
            self.draw_grid()
            self._update_action_buttons()

        except ValueError as error:
            self._update_action_buttons()
            messagebox.showerror("Parâmetros inválidos", str(error))
        except Exception as error:
            self._update_action_buttons()
            messagebox.showerror(
                "Erro inesperado",
                f"O algoritmo não pôde ser executado:\n{error}"
            )
