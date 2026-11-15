"""Contrato do padrão State (R1): EstadoLivro.

A classe declara TODOS os eventos do ciclo de vida com uma
implementação padrão que recusa a operação sem alterar o livro.
Cada estado concreto sobrescreve apenas os eventos válidos nele.
Assim, "reservar um exemplar em reparo" é impossível por omissão:
Reparando simplesmente não sobrescreve reservar.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from biblioteca.dominio.excecoes import OperacaoInvalidaException
from biblioteca.dominio.situacao import Situacao

if TYPE_CHECKING:  # só para type hints; evita dependência circular em runtime
    from biblioteca.dominio.modelos import Livro, Membro


class EstadoLivro:
    """Papel State. Os estados não têm atributos próprios, então cada
    um é uma instância única compartilhada (atributo INSTANCIA)."""

    # Eventos do ciclo de vida: a implementação padrão recusa.

    def reservar(self, livro: "Livro", membro: "Membro") -> None:
        raise self._recusa("reservar")

    def emprestar(self, livro: "Livro", membro: "Membro") -> None:
        raise self._recusa("emprestar")

    def renovar(self, livro: "Livro") -> None:
        raise self._recusa("renovar")

    def devolver(self, livro: "Livro") -> None:
        raise self._recusa("devolver")

    def aprovar_inspecao(self, livro: "Livro") -> None:
        raise self._recusa("aprovar_inspecao")

    def enviar_para_reparo(self, livro: "Livro") -> None:
        raise self._recusa("enviar_para_reparo")

    def concluir_reparo(self, livro: "Livro") -> None:
        raise self._recusa("concluir_reparo")

    def registrar_laudo_irrecuperavel(self, livro: "Livro") -> None:
        raise self._recusa("registrar_laudo_irrecuperavel")

    def situacao(self) -> Situacao:
        """Cada estado concreto informa sua Situacao."""
        raise NotImplementedError

    def _recusa(self, operacao: str) -> OperacaoInvalidaException:
        """Monta a exceção de recusa padrão, sem alterar nada."""
        return OperacaoInvalidaException(self.situacao(), operacao)
