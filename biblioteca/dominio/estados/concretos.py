"""Estados concretos do Livro (R1), seguindo a máquina de estados do
material da disciplina (Figura 1.2):

LIVRE -reservar-> RESERVADO -emprestar-> EMPRESTADO -renovar-> RENOVADO
EMPRESTADO/RENOVADO -devolver-> DEVOLVIDO
DEVOLVIDO -aprovarInspecao-> LIVRE | -enviarParaReparo-> REPARANDO
REPARANDO -concluirReparo-> LIVRE | -registrarLaudoIrrecuperavel-> INCINERADO

Cada classe fica neste único módulo porque as transições se referenciam
mutuamente (Livre -> Reservado -> ... -> Livre); em módulos separados
haveria import circular.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from biblioteca.dominio.estados.base import EstadoLivro
from biblioteca.dominio.excecoes import RenovacaoNegadaException
from biblioteca.dominio.regras import MAX_RENOVACOES, PRAZO_RENOVACAO_DIAS
from biblioteca.dominio.situacao import Situacao

if TYPE_CHECKING:
    from biblioteca.dominio.modelos import Livro, Membro


class Livre(EstadoLivro):
    INSTANCIA: "Livre"

    def reservar(self, livro: "Livro", membro: "Membro") -> None:
        if membro is None:  # defesa: o tratador valida o cadastro antes
            raise self._recusa("reservar")
        livro.reservante = membro
        livro._mudar_para(Reservado.INSTANCIA)

    def situacao(self) -> Situacao:
        return Situacao.LIVRE


class Reservado(EstadoLivro):
    INSTANCIA: "Reservado"

    def emprestar(self, livro: "Livro", membro: "Membro") -> None:
        if membro is None or livro.reservante is None or membro.id != livro.reservante.id:
            # empréstimo por outro membro que não o reservante: recusa
            raise self._recusa("emprestar")
        livro._definir_vencimento_inicial()
        livro._mudar_para(Emprestado.INSTANCIA)

    def situacao(self) -> Situacao:
        return Situacao.RESERVADO


class Emprestado(EstadoLivro):
    INSTANCIA: "Emprestado"

    def renovar(self, livro: "Livro") -> None:
        # Guarda ANTES de qualquer alteração: na recusa, vencimento e
        # contador ficam intactos.
        if livro.num_renovacoes >= MAX_RENOVACOES:
            raise RenovacaoNegadaException(livro.id)
        livro._prorrogar(PRAZO_RENOVACAO_DIAS)
        livro.num_renovacoes += 1
        livro._mudar_para(Renovado.INSTANCIA)

    def devolver(self, livro: "Livro") -> None:
        livro._mudar_para(Devolvido.INSTANCIA)

    def situacao(self) -> Situacao:
        return Situacao.EMPRESTADO


class Renovado(Emprestado):
    """Empréstimo já renovado. Herda renovar e devolver de Emprestado:
    a regra de renovação mora em um único método."""

    INSTANCIA: "Renovado"

    def situacao(self) -> Situacao:
        return Situacao.RENOVADO


class Devolvido(EstadoLivro):
    """Aguardando inspeção. reservar continua com a recusa herdada:
    o exemplar só volta a circular depois da inspeção."""

    INSTANCIA: "Devolvido"

    def aprovar_inspecao(self, livro: "Livro") -> None:
        livro._limpar_ciclo()
        livro._mudar_para(Livre.INSTANCIA)

    def enviar_para_reparo(self, livro: "Livro") -> None:
        livro._mudar_para(Reparando.INSTANCIA)

    def situacao(self) -> Situacao:
        return Situacao.DEVOLVIDO


class Reparando(EstadoLivro):
    INSTANCIA: "Reparando"

    def concluir_reparo(self, livro: "Livro") -> None:
        livro._limpar_ciclo()
        livro._mudar_para(Livre.INSTANCIA)

    def registrar_laudo_irrecuperavel(self, livro: "Livro") -> None:
        livro._mudar_para(Incinerado.INSTANCIA)

    def situacao(self) -> Situacao:
        return Situacao.REPARANDO


class Incinerado(EstadoLivro):
    """Estado final: nenhum evento é sobrescrito, tudo é recusado."""

    INSTANCIA: "Incinerado"

    def situacao(self) -> Situacao:
        return Situacao.INCINERADO


# Instâncias únicas compartilhadas (os estados não têm atributos).
Livre.INSTANCIA = Livre()
Reservado.INSTANCIA = Reservado()
Emprestado.INSTANCIA = Emprestado()
Renovado.INSTANCIA = Renovado()
Devolvido.INSTANCIA = Devolvido()
Reparando.INSTANCIA = Reparando()
Incinerado.INSTANCIA = Incinerado()
