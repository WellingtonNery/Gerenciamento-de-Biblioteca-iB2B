"""R1 (State): cenários do ciclo de vida do livro."""

from datetime import date, timedelta

import pytest

from biblioteca.dominio.excecoes import (
    OperacaoInvalidaException,
    RenovacaoNegadaException,
)
from biblioteca.dominio.modelos import PRAZO_EMPRESTIMO_DIAS, Livro, Membro
from biblioteca.dominio.situacao import Situacao


def novo_livro() -> Livro:
    return Livro(id="l1", titulo="Dom Casmurro", autor="Machado de Assis")


def novo_membro(id: str = "m1", nome: str = "Ana") -> Membro:
    return Membro(id=id, nome=nome, email=f"{id}@biblioteca.example")


def test_R01_fluxo_feliz_do_ciclo_completo():
    livro = novo_livro()
    ana = novo_membro()

    livro.reservar(ana)
    assert livro.situacao() == Situacao.RESERVADO
    assert livro.reservante is ana

    livro.emprestar(ana)
    assert livro.situacao() == Situacao.EMPRESTADO
    vencimento_inicial = date.today() + timedelta(days=PRAZO_EMPRESTIMO_DIAS)
    assert livro.vencimento == vencimento_inicial

    livro.renovar()
    assert livro.situacao() == Situacao.RENOVADO
    assert livro.num_renovacoes == 1
    assert livro.vencimento == vencimento_inicial + timedelta(days=30)

    livro.devolver()
    assert livro.situacao() == Situacao.DEVOLVIDO

    livro.aprovar_inspecao()
    assert livro.situacao() == Situacao.LIVRE
    # limparCiclo: exemplar pronto para um novo ciclo
    assert livro.num_renovacoes == 0
    assert livro.reservante is None
    assert livro.vencimento is None


def test_R01_terceira_renovacao_recusada():
    """Cenário de verificação do enunciado: RENOVADO com numRenovacoes = 2;
    a terceira chamada é recusada sem alterar vencimento nem contador."""
    livro = novo_livro()
    ana = novo_membro()
    livro.reservar(ana)
    livro.emprestar(ana)
    livro.renovar()
    livro.renovar()
    assert livro.situacao() == Situacao.RENOVADO
    assert livro.num_renovacoes == 2
    vencimento_antes = livro.vencimento

    with pytest.raises(RenovacaoNegadaException):
        livro.renovar()

    assert livro.situacao() == Situacao.RENOVADO
    assert livro.num_renovacoes == 2
    assert livro.vencimento == vencimento_antes


def test_R01_reserva_recusada_para_livro_devolvido_sem_inspecao():
    """Figura 1.4: Devolvido não sobrescreve reservar; a recusa herdada
    vale enquanto a inspeção não for registrada."""
    livro = novo_livro()
    ana = novo_membro()
    livro.reservar(ana)
    livro.emprestar(ana)
    livro.devolver()

    with pytest.raises(OperacaoInvalidaException) as erro:
        livro.reservar(novo_membro("m2", "Bia"))

    assert erro.value.situacao == Situacao.DEVOLVIDO
    assert erro.value.operacao == "reservar"
    assert livro.situacao() == Situacao.DEVOLVIDO


def test_R01_emprestimo_por_outro_membro_recusado():
    livro = novo_livro()
    livro.reservar(novo_membro("m1", "Ana"))

    with pytest.raises(OperacaoInvalidaException):
        livro.emprestar(novo_membro("m2", "Bia"))

    assert livro.situacao() == Situacao.RESERVADO
    assert livro.vencimento is None


def test_R01_laudo_irrecuperavel_leva_reparando_a_incinerado():
    livro = novo_livro()
    ana = novo_membro()
    livro.reservar(ana)
    livro.emprestar(ana)
    livro.devolver()
    livro.enviar_para_reparo()
    assert livro.situacao() == Situacao.REPARANDO

    livro.registrar_laudo_irrecuperavel()
    assert livro.situacao() == Situacao.INCINERADO


def test_R01_incinerado_recusa_qualquer_evento():
    livro = novo_livro()
    ana = novo_membro()
    livro.reservar(ana)
    livro.emprestar(ana)
    livro.devolver()
    livro.enviar_para_reparo()
    livro.registrar_laudo_irrecuperavel()

    for evento in (
        lambda: livro.reservar(ana),
        lambda: livro.emprestar(ana),
        livro.renovar,
        livro.devolver,
        livro.aprovar_inspecao,
        livro.enviar_para_reparo,
        livro.concluir_reparo,
        livro.registrar_laudo_irrecuperavel,
    ):
        with pytest.raises(OperacaoInvalidaException):
            evento()
    assert livro.situacao() == Situacao.INCINERADO


def test_R01_reparo_concluido_devolve_o_livro_ao_acervo():
    livro = novo_livro()
    ana = novo_membro()
    livro.reservar(ana)
    livro.emprestar(ana)
    livro.devolver()
    livro.enviar_para_reparo()

    livro.concluir_reparo()

    assert livro.situacao() == Situacao.LIVRE
    assert livro.num_renovacoes == 0
    assert livro.reservante is None
    assert livro.vencimento is None
