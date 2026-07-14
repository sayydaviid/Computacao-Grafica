from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class AlgorithmSpec:
    """Descreve a entrada esperada e a instrução exibida para um algoritmo."""

    name: str
    clicks: Optional[int]
    instruction: str
    auto_execute: bool = False
    parameter_keys: tuple[str, ...] = ()
    parameter_info: tuple[str, ...] = ()


ALGORITHMS: dict[str, AlgorithmSpec] = {
    "Bresenham": AlgorithmSpec(
        name="Bresenham",
        clicks=2,
        instruction="Clique no ponto inicial e no ponto final.",
        auto_execute=True,
        parameter_info=(
            "Ponto inicial: selecione na grade",
            "Ponto final: selecione na grade",
        ),
    ),
    "Círculo": AlgorithmSpec(
        name="Círculo",
        clicks=2,
        instruction="Clique no centro e depois em um ponto da circunferência.",
        auto_execute=True,
        parameter_info=(
            "Centro: selecione na grade",
            "Raio: definido pelo segundo ponto",
        ),
    ),
    "Elipse": AlgorithmSpec(
        name="Elipse",
        clicks=3,
        instruction="Clique no centro, no extremo horizontal e no extremo vertical.",
        auto_execute=True,
        parameter_info=(
            "Centro: selecione na grade",
            "Raio horizontal: definido pelo segundo ponto",
            "Raio vertical: definido pelo terceiro ponto",
        ),
    ),
    "Bézier grau 2": AlgorithmSpec(
        name="Bézier grau 2",
        clicks=3,
        instruction="Clique em P0, controle P1 e P2 final.",
        auto_execute=True,
        parameter_info=(
            "P0: ponto inicial",
            "P1: ponto de controle",
            "P2: ponto final",
        ),
    ),
    "Bézier grau 3": AlgorithmSpec(
        name="Bézier grau 3",
        clicks=4,
        instruction="Clique em P0, controles P1/P2 e P3 final.",
        auto_execute=True,
        parameter_info=(
            "P0: ponto inicial",
            "P1: primeiro ponto de controle",
            "P2: segundo ponto de controle",
            "P3: ponto final",
        ),
    ),
    "Polilinha": AlgorithmSpec(
        name="Polilinha",
        clicks=None,
        instruction="Clique em pelo menos 4 vértices; depois use Executar.",
        parameter_info=("Selecione pelo menos 4 vértices na grade.",),
    ),
    "Preenchimento recursivo": AlgorithmSpec(
        name="Preenchimento recursivo",
        clicks=None,
        instruction="Clique nos vértices do polígono. Informe a semente X/Y e execute.",
        parameter_keys=("seed_x", "seed_y"),
    ),
    "Preenchimento por varredura": AlgorithmSpec(
        name="Preenchimento por varredura",
        clicks=None,
        instruction="Clique nos vértices de um polígono irregular e execute.",
        parameter_info=("Selecione os vértices do polígono irregular na grade.",),
    ),
    "Recorte de linha": AlgorithmSpec(
        name="Recorte de linha",
        clicks=2,
        instruction="Defina a janela nos campos; clique nos dois extremos da linha.",
        parameter_keys=("xmin", "ymin", "xmax", "ymax"),
    ),
    "Recorte de polígono": AlgorithmSpec(
        name="Recorte de polígono",
        clicks=None,
        instruction="Defina a janela; clique nos vértices do polígono e execute.",
        parameter_keys=("xmin", "ymin", "xmax", "ymax"),
    ),
    "Translação": AlgorithmSpec(
        name="Translação",
        clicks=None,
        instruction="Clique nos vértices do polígono; informe Tx/Ty e execute.",
        parameter_keys=("tx", "ty"),
    ),
    "Escala": AlgorithmSpec(
        name="Escala",
        clicks=None,
        instruction="Clique nos vértices; informe Sx/Sy e ponto fixo; execute.",
        parameter_keys=("sx", "sy", "fixed_x", "fixed_y"),
    ),
    "Rotação": AlgorithmSpec(
        name="Rotação",
        clicks=None,
        instruction="Clique nos vértices; informe ângulo e pivô; execute.",
        parameter_keys=("angle", "pivot_x", "pivot_y"),
    ),
    "Projeção ortográfica": AlgorithmSpec(
        name="Projeção ortográfica",
        clicks=0,
        instruction="Usa um cubo 3D de exemplo. Clique em Executar.",
        parameter_info=("Projeção ortográfica do sólido 3D atual.",),
    ),
    "Projeção oblíqua": AlgorithmSpec(
        name="Projeção oblíqua",
        clicks=0,
        instruction="Usa um cubo 3D; informe ângulo e fator oblíquo.",
        parameter_keys=("angle", "oblique_scale"),
    ),
    "Projeção perspectiva": AlgorithmSpec(
        name="Projeção perspectiva",
        clicks=0,
        instruction="Usa um cubo 3D; informe a distância da câmera.",
        parameter_keys=("camera_distance",),
    ),
}
