"""Situação observável do Livro (R1).

A enumeração é o que as camadas externas enxergam; as classes de
estado (padrão State) são detalhe interno do domínio.
"""

from __future__ import annotations

from enum import Enum, auto


class Situacao(Enum):
    LIVRE = auto()
    RESERVADO = auto()
    EMPRESTADO = auto()
    RENOVADO = auto()
    DEVOLVIDO = auto()
    REPARANDO = auto()
    INCINERADO = auto()
