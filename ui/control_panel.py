from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from core.types import Point
from models.algorithm_spec import ALGORITHMS, AlgorithmSpec


class ControlPanel(ttk.Frame):
    """Painel lateral com seleção de algoritmo, parâmetros e lista de pontos."""

    PANEL_WIDTH = 340
    PARAMETER_DEFINITIONS: tuple[tuple[str, str, str], ...] = (
        ("Janela xmin", "xmin", "-5"),
        ("Janela ymin", "ymin", "-5"),
        ("Janela xmax", "xmax", "5"),
        ("Janela ymax", "ymax", "5"),
        ("Semente X", "seed_x", "0"),
        ("Semente Y", "seed_y", "0"),
        ("Tx", "tx", "2"),
        ("Ty", "ty", "2"),
        ("Sx", "sx", "1.5"),
        ("Sy", "sy", "1.5"),
        ("Fixo X", "fixed_x", "0"),
        ("Fixo Y", "fixed_y", "0"),
        ("Ângulo", "angle", "45"),
        ("Pivô X", "pivot_x", "0"),
        ("Pivô Y", "pivot_y", "0"),
        ("Fator obl.", "oblique_scale", "0.5"),
        ("Dist. câmera", "camera_distance", "14"),
    )

    def __init__(
        self,
        master: tk.Misc,
        algorithm_var: tk.StringVar,
        status_var: tk.StringVar,
        on_algorithm_changed: Callable[[], None],
        on_execute: Callable[[], None],
        on_undo: Callable[[], None],
        on_clear: Callable[[], None],
        on_view_3d: Callable[[], None],
    ) -> None:
        super().__init__(master, width=self.PANEL_WIDTH)
        self.algorithm_var = algorithm_var
        self.status_var = status_var
        self._on_algorithm_changed = on_algorithm_changed
        self._on_execute = on_execute
        self._on_undo = on_undo
        self._on_clear = on_clear
        self._on_view_3d = on_view_3d

        self.entries: dict[str, ttk.Entry] = {}
        self.parameter_widgets: dict[str, tuple[ttk.Label, ttk.Entry]] = {}
        self.parameter_info_labels: list[ttk.Label] = []
        self.params_frame: ttk.LabelFrame
        self.points_list: tk.Listbox
        self.execute_button: ttk.Button
        self.view_3d_button: ttk.Button
        self._execute_visible = True
        self._content_window: int | None = None

        self._build()

    def _build(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self._scroll_canvas = tk.Canvas(
            self,
            borderwidth=0,
            highlightthickness=0,
        )
        self._scrollbar = ttk.Scrollbar(
            self,
            orient=tk.VERTICAL,
            command=self._scroll_canvas.yview,
        )
        self._scroll_canvas.configure(yscrollcommand=self._scrollbar.set)

        self._scroll_canvas.grid(row=0, column=0, sticky="nsew")
        self._scrollbar.grid(row=0, column=1, sticky="ns")

        content = ttk.Frame(self._scroll_canvas)
        self._content_window = self._scroll_canvas.create_window(
            (0, 0),
            window=content,
            anchor="nw",
        )
        content.bind("<Configure>", lambda _: self._refresh_scroll_region())
        self._scroll_canvas.bind("<Configure>", self._on_scroll_canvas_configure)

        self._build_content(content)

    def _build_content(self, parent: ttk.Frame) -> None:
        ttk.Label(parent, text="Configurações", style="Title.TLabel").pack(anchor="w")

        ttk.Label(parent, text="Algoritmo", style="Section.TLabel").pack(anchor="w", pady=(12, 3))
        algo_combo = ttk.Combobox(
            parent,
            textvariable=self.algorithm_var,
            values=list(ALGORITHMS.keys()),
            state="readonly",
        )
        algo_combo.pack(fill=tk.X)
        algo_combo.bind("<<ComboboxSelected>>", lambda _: self._on_algorithm_changed())

        instruction = ttk.Label(
            parent,
            textvariable=self.status_var,
            wraplength=320,
            justify=tk.LEFT,
        )
        instruction.pack(fill=tk.X, pady=(8, 10))

        self.params_frame = ttk.LabelFrame(parent, text="Parâmetros", padding=8)
        self.params_frame.pack(fill=tk.X)
        self._build_parameter_widgets()

        buttons = ttk.Frame(parent)
        buttons.pack(fill=tk.X, pady=(12, 0))

        self.execute_button = ttk.Button(
            buttons,
            text="Executar algoritmo",
            style="Primary.TButton",
            command=self._on_execute,
        )
        self.execute_button.pack(fill=tk.X)

        self.view_3d_button = ttk.Button(
            buttons,
            text="Visualizar em 3D",
            command=self._on_view_3d,
            state=tk.DISABLED,
        )
        self.view_3d_button.pack(fill=tk.X, pady=(6, 0))

        ttk.Button(
            buttons,
            text="Desfazer último ponto",
            command=self._on_undo,
        ).pack(fill=tk.X, pady=(6, 0))

        ttk.Button(
            buttons,
            text="Limpar tudo",
            command=self._on_clear,
        ).pack(fill=tk.X, pady=(6, 0))

        points_frame = ttk.LabelFrame(parent, text="Pontos selecionados", padding=8)
        points_frame.pack(fill=tk.BOTH, expand=True, pady=(12, 0))

        self.points_list = tk.Listbox(points_frame, height=10)
        self.points_list.pack(fill=tk.BOTH, expand=True)

    def _build_parameter_widgets(self) -> None:
        for label_text, key, default in self.PARAMETER_DEFINITIONS:
            label = ttk.Label(self.params_frame, text=label_text)
            entry = ttk.Entry(self.params_frame, width=8)
            entry.insert(0, default)
            self.entries[key] = entry
            self.parameter_widgets[key] = (label, entry)

        self.params_frame.columnconfigure(0, weight=0)
        self.params_frame.columnconfigure(1, weight=1)
        self.params_frame.columnconfigure(2, weight=0)
        self.params_frame.columnconfigure(3, weight=1)

    def _update_parameter_area(self, spec: AlgorithmSpec) -> None:
        for label, entry in self.parameter_widgets.values():
            label.grid_forget()
            entry.grid_forget()

        for label in self.parameter_info_labels:
            label.destroy()
        self.parameter_info_labels.clear()

        row = 0
        for text in spec.parameter_info:
            label = ttk.Label(
                self.params_frame,
                text=text,
                wraplength=300,
                justify=tk.LEFT,
            )
            label.grid(row=row, column=0, columnspan=4, sticky="w", pady=2)
            self.parameter_info_labels.append(label)
            row += 1

        if spec.parameter_info and spec.parameter_keys:
            row += 1

        for index, key in enumerate(spec.parameter_keys):
            label, entry = self.parameter_widgets[key]
            row_index = row + index // 2
            column = 0 if index % 2 == 0 else 2
            entry_pad = (0, 8) if column == 0 else (0, 0)

            label.grid(row=row_index, column=column, sticky="w", padx=(0, 4), pady=2)
            entry.grid(row=row_index, column=column + 1, sticky="ew", padx=entry_pad, pady=2)

        self.after_idle(self._refresh_scroll_region)

    def _on_scroll_canvas_configure(self, event: tk.Event) -> None:
        if self._content_window is not None:
            self._scroll_canvas.itemconfigure(self._content_window, width=event.width)
        self._refresh_scroll_region()

    def _refresh_scroll_region(self) -> None:
        bbox = self._scroll_canvas.bbox("all")
        if bbox is None:
            return

        self._scroll_canvas.configure(scrollregion=bbox)
        content_height = bbox[3] - bbox[1]
        canvas_height = self._scroll_canvas.winfo_height()

        if content_height > canvas_height + 2:
            self._scrollbar.grid()
        else:
            self._scrollbar.grid_remove()
            self._scroll_canvas.yview_moveto(0)

    def update_for_algorithm(self, spec: AlgorithmSpec) -> None:
        """Atualiza controles cuja visibilidade depende da especificação."""

        self.set_execute_visible(not spec.auto_execute)
        self._update_parameter_area(spec)

    def set_execute_visible(self, visible: bool) -> None:
        """Mostra ou remove o botão de execução manual do layout."""

        if visible == self._execute_visible:
            return

        self._execute_visible = visible
        if visible:
            self.execute_button.pack(fill=tk.X, before=self.view_3d_button)
        else:
            self.execute_button.pack_forget()
        self.after_idle(self._refresh_scroll_region)

    def set_view_3d_enabled(self, enabled: bool) -> None:
        """Habilita o visualizador 3D somente quando há estado para exibir."""

        self.view_3d_button.configure(state=tk.NORMAL if enabled else tk.DISABLED)

    def value(self, key: str, cast: Callable = float):
        """Lê e converte um parâmetro mantendo a mensagem de erro original."""

        text = self.entries[key].get().strip()
        try:
            return cast(text)
        except ValueError as exc:
            raise ValueError(f"Valor inválido em '{key}': {text!r}") from exc

    def refresh_points_list(self, points: list[Point]) -> None:
        """Atualiza a lista visual de pontos selecionados."""

        self.points_list.delete(0, tk.END)
        for index, (x, y) in enumerate(points, start=1):
            self.points_list.insert(tk.END, f"P{index}: ({x}, {y})")
