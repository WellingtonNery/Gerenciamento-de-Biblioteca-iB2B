"""Entidades centrais do domínio.

O Livro é o Context do padrão State (R1): mantém os dados do ciclo
atual (vencimento, num_renovacoes, reservante) e delega cada evento
ao seu estado corrente. Quem decide o que é válido é o estado, nunca
um if/elif de situação espalhado pelo código.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta

from biblioteca.dominio.estados import concretos
from biblioteca.dominio.estados.base import EstadoLivro
from biblioteca.dominio.regras import (  # noqa: F401 (reexportadas)
    MAX_RENOVACOES,
    PRAZO_EMPRESTIMO_DIAS,
    PRAZO_RENOVACAO_DIAS,
)
from biblioteca.dominio.situacao import Situacao


@dataclass
class Membro:
    """Pessoa habilitada a reservar e retirar livros."""

    id: str
    nome: str
    email: str


@dataclass
class Livro:
    """Exemplar físico do acervo. Context do State."""

    id: str
    titulo: str
    autor: str
    vencimento: date | None = None
    num_renovacoes: int = 0
    reservante: Membro | None = None
    _estado: EstadoLivro = field(
        default_factory=lambda: concretos.Livre.INSTANCIA, repr=False
    )

    # Eventos do ciclo de vida: pura delegação ao estado corrente.

    def reservar(self, membro: Membro) -> None:
        self._estado.reservar(self, membro)

    def emprestar(self, membro: Membro) -> None:
        self._estado.emprestar(self, membro)

    def renovar(self) -> None:
        self._estado.renovar(self)

    def devolver(self) -> None:
        self._estado.devolver(self)

    def aprovar_inspecao(self) -> None:
        self._estado.aprovar_inspecao(self)

    def enviar_para_reparo(self) -> None:
        self._estado.enviar_para_reparo(self)

    def concluir_reparo(self) -> None:
        self._estado.concluir_reparo(self)

    def registrar_laudo_irrecuperavel(self) -> None:
        self._estado.registrar_laudo_irrecuperavel(self)

    def situacao(self) -> Situacao:
        return self._estado.situacao()

    # Operações internas, usadas apenas pelos estados (visibilidade de
    # pacote no UML).

    def _mudar_para(self, novo_estado: EstadoLivro) -> None:
        self._estado = novo_estado

    def _definir_vencimento_inicial(self) -> None:
        self.vencimento = date.today() + timedelta(days=PRAZO_EMPRESTIMO_DIAS)

    def _prorrogar(self, dias: int) -> None:
        assert self.vencimento is not None
        self.vencimento = self.vencimento + timedelta(days=dias)

    def _limpar_ciclo(self) -> None:
        """Prepara o exemplar para um novo ciclo de circulação."""
        self.num_renovacoes = 0
        self.reservante = None
        self.vencimento = None


@dataclass
class Emprestimo:
    """Vínculo entre um membro e um exemplar retirado (histórico de
    movimentação; usado a partir da Sprint 3)."""

    id: str
    id_livro: str
    id_membro: str
    data_retirada: date
    data_prevista: date
    num_renovacoes: int = 0

    @classmethod
    def novo(cls, id: str, id_livro: str, id_membro: str, retirada: date) -> "Emprestimo":
        """Cria um empréstimo com o prazo padrão de 30 dias."""
        return cls(
            id=id,
            id_livro=id_livro,
            id_membro=id_membro,
            data_retirada=retirada,
            data_prevista=retirada + timedelta(days=PRAZO_EMPRESTIMO_DIAS),
        )
