from __future__ import annotations

import math
import tkinter as tk
from typing import Iterable, Optional

from core.constants import GRID_SIZE, MAX_COORD, MIN_COORD
from core.types import Point

Point3D = tuple[float, float, float]
WorldFace = tuple[tuple[Point3D, Point3D, Point3D, Point3D], str, str]
LineSpec = tuple[Point3D, Point3D, str, int, tuple[int, int] | None]


def _create_cube_vertices(half_size: float, height: float) -> tuple[Point3D, ...]:
    return (
        (-half_size, -half_size, 0.0),
        (half_size, -half_size, 0.0),
        (half_size, half_size, 0.0),
        (-half_size, half_size, 0.0),
        (-half_size, -half_size, height),
        (half_size, -half_size, height),
        (half_size, half_size, height),
        (-half_size, half_size, height),
    )


RESULT_CUBE_VERTICES = _create_cube_vertices(0.42, 0.46)
INPUT_CUBE_VERTICES = _create_cube_vertices(0.32, 0.95)
CUBE_FACE_SPECS = (
    ((0, 1, 2, 3), 2),
    ((4, 7, 6, 5), 0),
    ((0, 4, 5, 1), 1),
    ((1, 5, 6, 2), 2),
    ((2, 6, 7, 3), 1),
    ((3, 7, 4, 0), 2),
)


class ThreeDViewer(tk.Toplevel):
    """Janela independente para visualização didática 3D da rasterização atual."""

    FRAME_MS = 33
    RESIZE_DEBOUNCE_MS = 100
    MIN_PITCH = math.radians(-89)
    MAX_PITCH = math.radians(89)
    RESULT_COLORS = ("#38bdf8", "#0ea5e9", "#0284c7")
    INPUT_COLORS = ("#fb923c", "#f97316", "#ea580c")

    def __init__(
        self,
        parent: tk.Misc,
        input_points: Iterable[Point],
        result_pixels: Iterable[Point],
        clipping_rect: Optional[tuple[int, int, int, int]],
    ) -> None:
        super().__init__(parent)
        self.title("Visualização 3D")
        self.geometry("900x680")
        self.minsize(640, 480)

        self.input_points = list(input_points)
        self.result_pixels = set(result_pixels)
        self.clipping_rect = clipping_rect

        self.yaw = math.radians(-38)
        self.pitch = math.radians(58)
        self.zoom = 24.0
        self._user_zoomed = False
        self._last_mouse: tuple[int, int] | None = None
        self._needs_render = True
        self._closed = False
        self._render_job: str | None = None
        self._resize_job: str | None = None

        self._world_faces: list[WorldFace] = []
        self._background_lines: list[LineSpec] = []
        self._input_label_points: list[tuple[float, float, float, str]] = []

        self.canvas = tk.Canvas(
            self,
            background="#f8fafc",
            highlightthickness=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self._prepare_scene()
        self._bind_events()
        self.protocol("WM_DELETE_WINDOW", self._close)
        self._start_render_loop()

    def show(self) -> None:
        """Exibe a janela e a traz para frente."""

        self.deiconify()
        self.lift()
        self.focus_set()

    def destroy(self) -> None:
        self._close()

    def _bind_events(self) -> None:
        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<ButtonPress-1>", self._on_mouse_down)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_release)
        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        self.canvas.bind("<Button-4>", self._on_mouse_wheel)
        self.canvas.bind("<Button-5>", self._on_mouse_wheel)

    def _prepare_scene(self) -> None:
        self._background_lines = self._build_grid_lines()
        if self.clipping_rect is not None:
            self._background_lines.extend(self._build_clipping_lines(self.clipping_rect))

        for x, y in sorted(self.result_pixels):
            self._add_cube_faces(
                center_x=x,
                center_y=y,
                base_vertices=RESULT_CUBE_VERTICES,
                colors=self.RESULT_COLORS,
                outline="#0369a1",
            )

        for index, (x, y) in enumerate(self.input_points, start=1):
            self._add_cube_faces(
                center_x=x,
                center_y=y,
                base_vertices=INPUT_CUBE_VERTICES,
                colors=self.INPUT_COLORS,
                outline="#c2410c",
            )
            self._input_label_points.append((x, y, 1.08, f"P{index}"))

    def _build_grid_lines(self) -> list[LineSpec]:
        lines: list[LineSpec] = []
        start = MIN_COORD - 0.5
        end = MAX_COORD + 0.5

        for index in range(GRID_SIZE + 1):
            value = start + index
            lines.append(((value, start, 0.0), (value, end, 0.0), "#cbd5e1", 1, None))
            lines.append(((start, value, 0.0), (end, value, 0.0), "#cbd5e1", 1, None))

        return lines

    def _build_clipping_lines(
        self,
        rect: tuple[int, int, int, int],
    ) -> list[LineSpec]:
        xmin, ymin, xmax, ymax = rect
        left = xmin - 0.5
        right = xmax + 0.5
        bottom = ymin - 0.5
        top = ymax + 0.5
        base_z = 0.06
        top_z = 0.72

        base = (
            (left, bottom, base_z),
            (right, bottom, base_z),
            (right, top, base_z),
            (left, top, base_z),
        )
        upper = tuple((x, y, top_z) for x, y, _ in base)
        lines: list[LineSpec] = []

        for corners in (base, upper):
            for index in range(4):
                lines.append(
                    (corners[index], corners[(index + 1) % 4], "#7c3aed", 2, (6, 4))
                )

        for lower, higher in zip(base, upper):
            lines.append((lower, higher, "#7c3aed", 2, (6, 4)))

        return lines

    def _add_cube_faces(
        self,
        *,
        center_x: float,
        center_y: float,
        base_vertices: tuple[Point3D, ...],
        colors: tuple[str, str, str],
        outline: str,
    ) -> None:
        for indices, color_index in CUBE_FACE_SPECS:
            face = tuple(
                (
                    base_vertices[index][0] + center_x,
                    base_vertices[index][1] + center_y,
                    base_vertices[index][2],
                )
                for index in indices
            )
            self._world_faces.append((face, colors[color_index], outline))

    def _on_mouse_down(self, event: tk.Event) -> None:
        self._last_mouse = (event.x, event.y)

    def _on_mouse_drag(self, event: tk.Event) -> None:
        if self._last_mouse is None:
            self._last_mouse = (event.x, event.y)
            return

        last_x, last_y = self._last_mouse
        dx = event.x - last_x
        dy = event.y - last_y
        self._last_mouse = (event.x, event.y)

        self.yaw += dx * 0.01
        self.pitch = max(self.MIN_PITCH, min(self.MAX_PITCH, self.pitch + dy * 0.01))
        self._mark_needs_render()

    def _on_mouse_release(self, _event: tk.Event) -> None:
        self._last_mouse = None
        self._mark_needs_render()

    def _on_mouse_wheel(self, event: tk.Event) -> None:
        direction = 1
        if getattr(event, "num", None) == 5 or getattr(event, "delta", 0) < 0:
            direction = -1

        factor = 1.1 if direction > 0 else 0.9
        self.zoom = max(8.0, min(90.0, self.zoom * factor))
        self._user_zoomed = True
        self._mark_needs_render()

    def _on_resize(self, event: tk.Event) -> None:
        if event.widget is not self.canvas or self._closed:
            return

        if self._resize_job is not None:
            self._cancel_after(self._resize_job)
        self._resize_job = self.after(self.RESIZE_DEBOUNCE_MS, self._finish_resize)

    def _finish_resize(self) -> None:
        self._resize_job = None
        self._mark_needs_render()

    def _mark_needs_render(self) -> None:
        if not self._closed:
            self._needs_render = True

    def _start_render_loop(self) -> None:
        if self._render_job is None and not self._closed:
            self._render_job = self.after(self.FRAME_MS, self._render_loop)

    def _render_loop(self) -> None:
        self._render_job = None
        if self._closed:
            return

        if self._needs_render:
            self._render_scene()
            self._needs_render = False

        if not self._closed:
            self._render_job = self.after(self.FRAME_MS, self._render_loop)

    def _render_scene(self) -> None:
        if self._closed:
            return

        try:
            canvas_width = max(self.canvas.winfo_width(), 1)
            canvas_height = max(self.canvas.winfo_height(), 1)
            self.canvas.delete("all")
        except tk.TclError:
            self._closed = True
            return

        if not self._user_zoomed:
            self.zoom = max(10.0, min(canvas_width / 34.0, canvas_height / 28.0))

        cos_yaw = math.cos(self.yaw)
        sin_yaw = math.sin(self.yaw)
        cos_pitch = math.cos(self.pitch)
        sin_pitch = math.sin(self.pitch)
        center_x = canvas_width / 2
        center_y = canvas_height / 2

        for line in self._background_lines:
            self._draw_projected_line(
                line,
                cos_yaw,
                sin_yaw,
                cos_pitch,
                sin_pitch,
                center_x,
                center_y,
            )

        drawables: list[tuple[float, tuple[float, ...], str, str]] = []
        for vertices, fill, outline in self._world_faces:
            coords: list[float] = []
            depth_total = 0.0
            for x, y, z in vertices:
                screen_x, screen_y, depth = self._project_point(
                    x,
                    y,
                    z,
                    cos_yaw,
                    sin_yaw,
                    cos_pitch,
                    sin_pitch,
                    center_x,
                    center_y,
                )
                coords.extend((screen_x, screen_y))
                depth_total += depth
            drawables.append((depth_total * 0.25, tuple(coords), fill, outline))

        drawables.sort(key=lambda item: item[0])
        for _, coords, fill, outline in drawables:
            self.canvas.create_polygon(*coords, fill=fill, outline=outline)

        self._draw_input_labels(
            cos_yaw,
            sin_yaw,
            cos_pitch,
            sin_pitch,
            center_x,
            center_y,
        )

    def _draw_projected_line(
        self,
        line: LineSpec,
        cos_yaw: float,
        sin_yaw: float,
        cos_pitch: float,
        sin_pitch: float,
        center_x: float,
        center_y: float,
    ) -> None:
        start, end, fill, width, dash = line
        x1, y1, _ = self._project_point(
            start[0], start[1], start[2],
            cos_yaw, sin_yaw, cos_pitch, sin_pitch, center_x, center_y,
        )
        x2, y2, _ = self._project_point(
            end[0], end[1], end[2],
            cos_yaw, sin_yaw, cos_pitch, sin_pitch, center_x, center_y,
        )

        if dash is not None:
            self.canvas.create_line(x1, y1, x2, y2, fill=fill, width=width, dash=dash)
        else:
            self.canvas.create_line(x1, y1, x2, y2, fill=fill, width=width)

    def _project_point(
        self,
        x: float,
        y: float,
        z: float,
        cos_yaw: float,
        sin_yaw: float,
        cos_pitch: float,
        sin_pitch: float,
        center_x: float,
        center_y: float,
    ) -> tuple[float, float, float]:
        rotated_x = x * cos_yaw - y * sin_yaw
        rotated_y = x * sin_yaw + y * cos_yaw
        depth = rotated_y * cos_pitch - z * sin_pitch
        rotated_z = rotated_y * sin_pitch + z * cos_pitch
        return center_x + rotated_x * self.zoom, center_y - rotated_z * self.zoom, depth

    def _draw_input_labels(
        self,
        cos_yaw: float,
        sin_yaw: float,
        cos_pitch: float,
        sin_pitch: float,
        center_x: float,
        center_y: float,
    ) -> None:
        for x, y, z, text in self._input_label_points:
            screen_x, screen_y, _ = self._project_point(
                x,
                y,
                z,
                cos_yaw,
                sin_yaw,
                cos_pitch,
                sin_pitch,
                center_x,
                center_y,
            )
            self.canvas.create_text(
                screen_x,
                screen_y - 7,
                text=text,
                fill="#7c2d12",
                font=("Arial", 10, "bold"),
            )

    def _close(self) -> None:
        if self._closed:
            return

        self._closed = True
        if self._render_job is not None:
            self._cancel_after(self._render_job)
            self._render_job = None
        if self._resize_job is not None:
            self._cancel_after(self._resize_job)
            self._resize_job = None
        try:
            super().destroy()
        except tk.TclError:
            pass

    def _cancel_after(self, job: str | None) -> None:
        if job is None:
            return

        try:
            self.after_cancel(job)
        except tk.TclError:
            pass
