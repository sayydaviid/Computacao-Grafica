from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class AlgorithmSpec:
    """Descreve a entrada esperada e a instrução exibida para um algoritmo."""

    name: str
    clicks: Optional[int]
    instruction: str


ALGORITHMS: dict[str, AlgorithmSpec] = {
    "Bresenham": AlgorithmSpec(
        "Bresenham", 2, "Clique no ponto inicial e no ponto final."
    ),
    "Círculo": AlgorithmSpec(
        "Círculo", 2, "Clique no centro e depois em um ponto da circunferência."
    ),
    "Elipse": AlgorithmSpec(
        "Elipse", 3, "Clique no centro, no extremo horizontal e no extremo vertical."
    ),
    "Bézier grau 2": AlgorithmSpec(
        "Bézier grau 2", 3, "Clique em P0, controle P1 e P2 final."
    ),
    "Bézier grau 3": AlgorithmSpec(
        "Bézier grau 3", 4, "Clique em P0, controles P1/P2 e P3 final."
    ),
    "Polilinha": AlgorithmSpec(
        "Polilinha", None, "Clique em pelo menos 4 vértices; depois use Executar."
    ),
    "Preenchimento recursivo": AlgorithmSpec(
        "Preenchimento recursivo", None,
        "Clique nos vértices do polígono. Informe a semente X/Y e execute."
    ),
    "Preenchimento por varredura": AlgorithmSpec(
        "Preenchimento por varredura", None,
        "Clique nos vértices de um polígono irregular e execute."
    ),
    "Recorte de linha": AlgorithmSpec(
        "Recorte de linha", 2,
        "Defina a janela nos campos; clique nos dois extremos da linha."
    ),
    "Recorte de polígono": AlgorithmSpec(
        "Recorte de polígono", None,
        "Defina a janela; clique nos vértices do polígono e execute."
    ),
    "Translação": AlgorithmSpec(
        "Translação", None,
        "Clique nos vértices do polígono; informe Tx/Ty e execute."
    ),
    "Escala": AlgorithmSpec(
        "Escala", None,
        "Clique nos vértices; informe Sx/Sy e ponto fixo; execute."
    ),
    "Rotação": AlgorithmSpec(
        "Rotação", None,
        "Clique nos vértices; informe ângulo e pivô; execute."
    ),
    "Projeção ortográfica": AlgorithmSpec(
        "Projeção ortográfica", 0, "Usa um cubo 3D de exemplo. Clique em Executar."
    ),
    "Projeção oblíqua": AlgorithmSpec(
        "Projeção oblíqua", 0, "Usa um cubo 3D; informe ângulo e fator oblíquo."
    ),
    "Projeção perspectiva": AlgorithmSpec(
        "Projeção perspectiva", 0, "Usa um cubo 3D; informe a distância da câmera."
    ),
}
