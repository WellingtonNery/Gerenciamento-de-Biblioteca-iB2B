"""Sprint 0: garante que o pacote importa e as fundações funcionam."""

from datetime import date, timedelta

from biblioteca.dominio.modelos import (
    MAX_RENOVACOES,
    PRAZO_EMPRESTIMO_DIAS,
    Emprestimo,
    Livro,
    Membro,
)
from biblioteca.dominio.resultado import Resultado


def test_resultado_ok_carrega_dados():
    resultado = Resultado.ok("empréstimo realizado", id_emprestimo="e1")
    assert resultado.sucesso
    assert resultado.dados["id_emprestimo"] == "e1"


def test_resultado_recusado_tem_motivo():
    resultado = Resultado.recusado("terceira renovação não permitida")
    assert not resultado.sucesso
    assert "renovação" in resultado.mensagem


def test_emprestimo_novo_calcula_prazo_de_30_dias():
    retirada = date(2026, 11, 15)
    emprestimo = Emprestimo.novo("e1", id_livro="l1", id_membro="m1", retirada=retirada)
    assert emprestimo.data_prevista == retirada + timedelta(days=PRAZO_EMPRESTIMO_DIAS)
    assert emprestimo.num_renovacoes == 0
    assert MAX_RENOVACOES == 2


def test_entidades_basicas_existem():
    livro = Livro(id="l1", titulo="Dom Casmurro", autor="Machado de Assis")
    membro = Membro(id="m1", nome="João Pedro", email="joao@example.com")
    assert livro.titulo == "Dom Casmurro"
    assert membro.nome == "João Pedro"
