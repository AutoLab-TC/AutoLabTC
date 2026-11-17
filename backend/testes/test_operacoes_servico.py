import shutil

import pytest

from api.nucleo.dto.resposta_operacao import RespostaOperacao
from api.nucleo.utilitario.utilitarios_jff import converter_jff_para_automato
from api.servicos import operacoes_servico
from api.servicos.operacoes_servico import complemento, concatenacao

JFF = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<structure>
    <type>fa</type>
    <automaton>
        <state id="0" name="q0">
            <x>100</x>
            <y>100</y>
            <initial/>
            <final/>
        </state>
        <state id="1" name="q1">
            <x>200</x>
            <y>100</y>
        </state>
        <transition>
            <from>0</from>
            <to>1</to>
            <read>a</read>
        </transition>
    </automaton>
</structure>
"""


@pytest.mark.skipif(
    shutil.which("pdflatex") is None,
    reason="pdflatex não está disponível no PATH.",
)
def test_complemento():
    resultado = complemento(JFF.encode("utf-8"))

    assert isinstance(resultado, RespostaOperacao)
    assert "<structure>" in resultado.arquivo_jff

    automato = converter_jff_para_automato(resultado.arquivo_jff)

    assert automato.eh_afd()


@pytest.mark.skipif(
    shutil.which("pdflatex") is None,
    reason="pdflatex não está disponível no PATH.",
)
def test_complemento_retorna_relatorio_pdf():
    resultado = complemento(JFF.encode("utf-8"))

    assert resultado.relatorio_pdf.startswith(b"%PDF")
    assert len(resultado.relatorio_pdf) > 1000


@pytest.mark.skipif(
    shutil.which("pdflatex") is None,
    reason="pdflatex não está disponível no PATH.",
)
def test_complemento_com_alfabeto_externo():
    resultado = complemento(JFF.encode("utf-8"), alfabeto='["a","b"]')

    assert isinstance(resultado, RespostaOperacao)

    automato = converter_jff_para_automato(resultado.arquivo_jff)

    assert automato.eh_afd()
    assert {"a", "b"}.issubset(automato.alfabeto)


@pytest.mark.skipif(
    shutil.which("pdflatex") is None,
    reason="pdflatex não está disponível no PATH.",
)
def test_complemento_alfabeto_invalido_usa_derivado():
    resultado = complemento(JFF.encode("utf-8"), alfabeto="a,b")

    assert isinstance(resultado, RespostaOperacao)

    automato = converter_jff_para_automato(resultado.arquivo_jff)

    assert automato.eh_afd()
    assert automato.alfabeto == {"a"}


@pytest.mark.skipif(
    shutil.which("pdflatex") is None,
    reason="pdflatex não está disponível no PATH.",
)
def test_concatenacao():
    resultado = concatenacao(JFF.encode("utf-8"), JFF.encode("utf-8"))

    assert isinstance(resultado, RespostaOperacao)
    assert "<structure>" in resultado.arquivo_jff

    automato = converter_jff_para_automato(resultado.arquivo_jff)

    assert any(transicao.simbolo is None for transicao in automato.transicoes)
    assert automato.alfabeto == {"a"}


def test_concatenacao_repassa_alfabetos(monkeypatch):
    alfabetos_recebidos = []

    def converter(jff, alfabeto=None):
        alfabetos_recebidos.append(alfabeto)
        return converter_jff_para_automato(jff, alfabeto=alfabeto)

    monkeypatch.setattr(operacoes_servico, "converter_jff_para_automato", converter)
    monkeypatch.setattr(
        operacoes_servico, "gerar_pdf", lambda resultado, titulo: b"%PDF-1.4\n"
    )

    concatenacao(
        JFF.encode("utf-8"),
        JFF.encode("utf-8"),
        alfabeto1='["a","b"]',
        alfabeto2="a,b",
    )

    assert alfabetos_recebidos == [{"a", "b"}, None]
