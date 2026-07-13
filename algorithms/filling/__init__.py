"""Algoritmos de preenchimento."""

from algorithms.filling.flood_fill import flood_fill
from algorithms.filling.scanline import point_in_polygon, scanline_fill

__all__ = ["flood_fill", "point_in_polygon", "scanline_fill"]
