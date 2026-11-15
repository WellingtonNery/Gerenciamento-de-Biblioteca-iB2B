"""Exceções de domínio (R1).

Elas nascem no domínio e são convertidas em Resultado pelos
tratadores (Sprint 3). Exceção crua não atravessa a fachada.
"""

from __future__ import annotations

from biblioteca.dominio.regras import MAX_RENOVACOES
from biblioteca.dominio.situacao import Situacao


class ErroDeDominio(Exception):
    """Base de todas as recusas de regra de negócio."""


class OperacaoInvalidaException(ErroDeDominio):
    """Evento não permitido para a situação atual do livro.

    É lançada ANTES de qualquer alteração: o livro permanece intacto.
    """

    def __init__(self, situacao: Situacao, operacao: str) -> None:
        self.situacao = situacao
        self.operacao = operacao
        super().__init__(
            f"operação '{operacao}' inválida para livro na situação {situacao.name}"
        )


class RenovacaoNegadaException(ErroDeDominio):
    """Terceira renovação: a guarda numRenovacoes < 2 falhou."""

    def __init__(self, id_livro: str) -> None:
        self.id_livro = id_livro
        super().__init__(
            f"limite de {MAX_RENOVACOES} renovações atingido para o livro {id_livro}"
        )
