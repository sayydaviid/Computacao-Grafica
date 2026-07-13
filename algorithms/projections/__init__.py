"""Projeções 3D e rasterização de suas arestas."""

from algorithms.projections.edges import rasterize_edges
from algorithms.projections.oblique import oblique_projection
from algorithms.projections.orthographic import orthographic_projection
from algorithms.projections.perspective import perspective_projection

__all__ = [
    "oblique_projection",
    "orthographic_projection",
    "perspective_projection",
    "rasterize_edges",
]
