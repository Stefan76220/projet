"""Agregat Projet public de TomeLinea V5.

V5-02 encapsule ProjectV4 sans le recopier. Cela preserve exactement
la separation Source -> Analyse -> Propositions -> Livre deja validee,
tout en donnant aux futurs modules V5 un nom d'API stable.
"""

from src.v4.project import ProjectV4 as Project

__all__ = ["Project"]