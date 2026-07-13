"""Algoritmos de recorte."""

from algorithms.clipping.line_clipping import cohen_sutherland_clip
from algorithms.clipping.polygon_clipping import sutherland_hodgman_clip

__all__ = ["cohen_sutherland_clip", "sutherland_hodgman_clip"]
