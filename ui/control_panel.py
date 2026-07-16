from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from core.types import Point
from models.algorithm_spec import ALGORITHMS, AlgorithmSpec


class ControlPanel(ttk.Frame):
    """Painel lateral com seleção de algoritmo, parâmetros e lista de pontos."""

    PANEL_WIDTH = 340
    HUGO_ALGORITHMS: tuple[str, ...] = (
        "Bresenham",
        "Círculo",
        "Elipse",
        "Bézier grau 2",
        "Bézier grau 3",
        "Polilinha",
        "Translação",
        "Rotação",
        "Escala",
    )
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
        self.parameter_defaults = {
            key: default for _, key, default in self.PARAMETER_DEFINITIONS
        }

        self.entries: dict[str, ttk.Entry] = {}
        self.parameter_widgets: dict[str, tuple[ttk.Label, ttk.Entry]] = {}
        self.parameter_info_labels: list[ttk.Label] = []
        self.params_frame: ttk.LabelFrame
        self.points_list: tk.Listbox
        self.execute_button: ttk.Button
        self.view_3d_button: ttk.Button
        self.algorithm_button: ttk.Menubutton
        self.algorithm_dropdown: tk.Toplevel | None = None
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
        self.algorithm_button = ttk.Menubutton(
            parent,
            textvariable=self.algorithm_var,
        )
        self.algorithm_button.bind("<Button-1>", self._toggle_algorithm_dropdown)
        self.algorithm_button.bind("<Return>", self._toggle_algorithm_dropdown)
        self.algorithm_button.bind("<space>", self._toggle_algorithm_dropdown)
        self.algorithm_button.pack(fill=tk.X)

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

    def _algorithm_groups(self) -> tuple[tuple[str, tuple[str, ...]], ...]:
        selected_hugo = set(self.HUGO_ALGORITHMS)
        return (
            ("Hugo", self.HUGO_ALGORITHMS),
            (
                "David",
                tuple(name for name in ALGORITHMS if name not in selected_hugo),
            ),
        )

    def _toggle_algorithm_dropdown(self, event: tk.Event) -> str:
        if self.algorithm_dropdown is not None and self.algorithm_dropdown.winfo_exists():
            self._close_algorithm_dropdown()
        else:
            self._open_algorithm_dropdown()

        return "break"

    def _open_algorithm_dropdown(self) -> None:
        if self.algorithm_dropdown is not None and self.algorithm_dropdown.winfo_exists():
            return

        border_color = "#9ca3af"
        dropdown_background = "#ffffff"
        header_background = "#e5e7eb"
        header_foreground = "#111827"
        option_background = "#ffffff"
        option_foreground = "#111827"
        selected_background = "#dbeafe"
        selected_foreground = "#111827"
        hover_background = "#2563eb"
        hover_foreground = "#ffffff"

        dropdown = tk.Toplevel(self)
        dropdown.withdraw()
        dropdown.overrideredirect(True)
        dropdown.transient(self.winfo_toplevel())
        dropdown.configure(background=border_color)
        dropdown.bind("<Escape>", lambda _: self._close_algorithm_dropdown())
        dropdown.bind("<FocusOut>", lambda _: self.after(100, self._close_algorithm_dropdown))
        dropdown.bind("<ButtonPress>", self._close_algorithm_dropdown_if_outside, add="+")
        self.algorithm_dropdown = dropdown

        content = tk.Frame(dropdown, background=dropdown_background, borderwidth=1)
        content.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        for group_index, (group_name, algorithms) in enumerate(self._algorithm_groups()):
            if group_index > 0:
                separator = tk.Frame(content, height=1, background=border_color)
                separator.pack(fill=tk.X)

            header = tk.Label(
                content,
                text=group_name,
                anchor=tk.CENTER,
                background=header_background,
                foreground=header_foreground,
                font=("Arial", 10, "bold"),
                padx=8,
                pady=4,
                takefocus=0,
            )
            header.pack(fill=tk.X)

            for algorithm_name in algorithms:
                option = tk.Label(
                    content,
                    text=algorithm_name,
                    anchor=tk.W,
                    cursor="hand2",
                    padx=10,
                    pady=4,
                    takefocus=1,
                )
                self._style_algorithm_option(
                    option,
                    selected=algorithm_name == self.algorithm_var.get(),
                    option_background=option_background,
                    option_foreground=option_foreground,
                    selected_background=selected_background,
                    selected_foreground=selected_foreground,
                )
                option.bind(
                    "<Enter>",
                    lambda _, widget=option: widget.configure(
                        background=hover_background,
                        foreground=hover_foreground,
                    ),
                )
                option.bind(
                    "<Leave>",
                    lambda _,
                    name=algorithm_name,
                    widget=option: self._style_algorithm_option(
                        widget,
                        selected=name == self.algorithm_var.get(),
                        option_background=option_background,
                        option_foreground=option_foreground,
                        selected_background=selected_background,
                        selected_foreground=selected_foreground,
                    ),
                )
                option.bind(
                    "<ButtonRelease-1>",
                    lambda _, name=algorithm_name: self._select_algorithm(name),
                )
                option.bind(
                    "<Return>",
                    lambda _, name=algorithm_name: self._select_algorithm(name),
                )
                option.pack(fill=tk.X)

        self.update_idletasks()
        width = self.algorithm_button.winfo_width()
        x = self.algorithm_button.winfo_rootx()
        y = self.algorithm_button.winfo_rooty() + self.algorithm_button.winfo_height()
        dropdown.update_idletasks()
        dropdown.geometry(f"{width}x{dropdown.winfo_reqheight()}+{x}+{y}")
        dropdown.deiconify()
        dropdown.lift()
        dropdown.focus_set()

    def _style_algorithm_option(
        self,
        widget: tk.Label,
        *,
        selected: bool,
        option_background: str,
        option_foreground: str,
        selected_background: str,
        selected_foreground: str,
    ) -> None:
        if selected:
            widget.configure(
                background=selected_background,
                foreground=selected_foreground,
            )
        else:
            widget.configure(
                background=option_background,
                foreground=option_foreground,
            )

    def _close_algorithm_dropdown(self) -> None:
        dropdown = self.algorithm_dropdown
        self.algorithm_dropdown = None
        if dropdown is None or not dropdown.winfo_exists():
            return

        try:
            current_grab = dropdown.grab_current()
            if current_grab is not None and str(current_grab) == str(dropdown):
                current_grab.grab_release()
            dropdown.destroy()
        except tk.TclError:
            pass

    def _close_algorithm_dropdown_if_outside(self, event: tk.Event) -> None:
        dropdown = self.algorithm_dropdown
        if dropdown is None or not dropdown.winfo_exists():
            return

        x = event.x_root
        y = event.y_root
        inside_x = dropdown.winfo_rootx() <= x < dropdown.winfo_rootx() + dropdown.winfo_width()
        inside_y = dropdown.winfo_rooty() <= y < dropdown.winfo_rooty() + dropdown.winfo_height()
        if not (inside_x and inside_y):
            self._close_algorithm_dropdown()

    def _select_algorithm(self, algorithm_name: str) -> None:
        if algorithm_name not in ALGORITHMS:
            return

        self._close_algorithm_dropdown()
        self.algorithm_var.set(algorithm_name)
        self._on_algorithm_changed()

    def _build_parameter_widgets(self) -> None:
        for label_text, key, default in self.PARAMETER_DEFINITIONS:
            label = ttk.Label(self.params_frame, text=label_text)
            entry = ttk.Entry(self.params_frame, width=8, takefocus=True)
            entry.insert(0, default)
            entry.bind("<Button-1>", lambda e: e.widget.after_idle(e.widget.focus_force))
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
            entry.state(["!disabled", "!readonly"])
            entry.configure(takefocus=True)
            entry.delete(0, tk.END)
            entry.insert(0, self.parameter_defaults[key])
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
