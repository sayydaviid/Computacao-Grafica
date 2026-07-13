from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from core.types import Point
from models.algorithm_spec import ALGORITHMS


class ControlPanel(ttk.Frame):
    """Painel lateral com seleção de algoritmo, parâmetros e lista de pontos."""

    def __init__(
        self,
        master: tk.Misc,
        algorithm_var: tk.StringVar,
        status_var: tk.StringVar,
        on_algorithm_changed: Callable[[], None],
        on_execute: Callable[[], None],
        on_undo: Callable[[], None],
        on_clear: Callable[[], None],
    ) -> None:
        super().__init__(master, width=340)
        self.algorithm_var = algorithm_var
        self.status_var = status_var
        self._on_algorithm_changed = on_algorithm_changed
        self._on_execute = on_execute
        self._on_undo = on_undo
        self._on_clear = on_clear
        self.entries: dict[str, ttk.Entry] = {}
        self.points_list: tk.Listbox

        self._build()

    def _build(self) -> None:
        ttk.Label(self, text="Configurações", style="Title.TLabel").pack(anchor="w")

        ttk.Label(self, text="Algoritmo", style="Section.TLabel").pack(anchor="w", pady=(12, 3))
        algo_combo = ttk.Combobox(
            self,
            textvariable=self.algorithm_var,
            values=list(ALGORITHMS.keys()),
            state="readonly",
        )
        algo_combo.pack(fill=tk.X)
        algo_combo.bind("<<ComboboxSelected>>", lambda _: self._on_algorithm_changed())

        instruction = ttk.Label(
            self,
            textvariable=self.status_var,
            wraplength=320,
            justify=tk.LEFT,
        )
        instruction.pack(fill=tk.X, pady=(8, 10))

        params_frame = ttk.LabelFrame(self, text="Parâmetros", padding=8)
        params_frame.pack(fill=tk.X)

        defaults = {
            "xmin": "-5", "ymin": "-5", "xmax": "5", "ymax": "5",
            "seed_x": "0", "seed_y": "0",
            "tx": "2", "ty": "2",
            "sx": "1.5", "sy": "1.5",
            "fixed_x": "0", "fixed_y": "0",
            "angle": "45", "pivot_x": "0", "pivot_y": "0",
            "oblique_scale": "0.5", "camera_distance": "14",
        }

        rows = [
            ("Janela xmin", "xmin", "Janela ymin", "ymin"),
            ("Janela xmax", "xmax", "Janela ymax", "ymax"),
            ("Semente X", "seed_x", "Semente Y", "seed_y"),
            ("Tx", "tx", "Ty", "ty"),
            ("Sx", "sx", "Sy", "sy"),
            ("Fixo X", "fixed_x", "Fixo Y", "fixed_y"),
            ("Ângulo", "angle", "Pivô X", "pivot_x"),
            ("Pivô Y", "pivot_y", "Fator obl.", "oblique_scale"),
            ("Dist. câmera", "camera_distance", "", ""),
        ]

        for row_index, (label1, key1, label2, key2) in enumerate(rows):
            ttk.Label(params_frame, text=label1).grid(row=row_index, column=0, sticky="w", padx=(0, 4), pady=2)
            e1 = ttk.Entry(params_frame, width=8)
            e1.insert(0, defaults[key1])
            e1.grid(row=row_index, column=1, sticky="ew", padx=(0, 8), pady=2)
            self.entries[key1] = e1

            if key2:
                ttk.Label(params_frame, text=label2).grid(row=row_index, column=2, sticky="w", padx=(0, 4), pady=2)
                e2 = ttk.Entry(params_frame, width=8)
                e2.insert(0, defaults[key2])
                e2.grid(row=row_index, column=3, sticky="ew", pady=2)
                self.entries[key2] = e2

        for col in range(4):
            params_frame.columnconfigure(col, weight=1)

        buttons = ttk.Frame(self)
        buttons.pack(fill=tk.X, pady=(12, 0))

        ttk.Button(
            buttons,
            text="Executar algoritmo",
            style="Primary.TButton",
            command=self._on_execute,
        ).pack(fill=tk.X)

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

        points_frame = ttk.LabelFrame(self, text="Pontos selecionados", padding=8)
        points_frame.pack(fill=tk.BOTH, expand=True, pady=(12, 0))

        self.points_list = tk.Listbox(points_frame, height=10)
        self.points_list.pack(fill=tk.BOTH, expand=True)

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
