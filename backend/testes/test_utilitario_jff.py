import api.nucleo.automato_finito
import api.nucleo.estado
import api.nucleo.excecoes
import api.nucleo.transicao
from api.nucleo.utilitario.utilitarios_jff import (
    converter_automato_para_jff,
    converter_jff_para_automato,
    salvar_jff,
    serializar,

)

JFF_SIMPLES = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<structure>
    <type>fa</type>
    <automaton>
        <state id="0" name="q0">
            <x>100.0</x>
            <y>200.0</y>
            <initial/>
        </state>
        <state id="1" name="q1">
            <x>300.0</x>
            <y>200.0</y>
            <final/>
        </state>
        <transition>
            <from>0</from>
            <to>1</to>
            <read>a</read>
        </transition>
        <transition>
            <from>1</from>
            <to>1</to>
            <read>b</read>
        </transition>
    </automaton>
</structure>
"""


JFF_EPSILON = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<structure>
    <type>fa</type>
    <automaton>
        <state id="0" name="q0">
            <x>100.0</x>
            <y>200.0</y>
            <initial/>
        </state>
        <state id="1" name="q1">
            <x>300.0</x>
            <y>200.0</y>
            <final/>
        </state>
        <transition>
            <from>0</from>
            <to>1</to>
            <read/>
        </transition>
    </automaton>
</structure>
"""


def test_converter_automato_simples():
    automato = converter_jff_para_automato(JFF_SIMPLES)

    automato.validar()  # não deve lançar
    assert sorted(e.nome for e in automato.estados) == ["q0", "q1"]
    assert automato.alfabeto == {"a", "b"}
    assert len(automato.transicoes) == 2
    assert automato.estado_inicial.nome == "q0"
    assert [e.nome for e in automato.estados_finais] == ["q1"]


def test_converter_transicao_epsilon():
    automato = converter_jff_para_automato(JFF_EPSILON)

    assert automato.transicoes[0].simbodo is None
    assert automato.alfabeto == set()


def test_converter_estado_sem_name_usa_id():
    jff = JFF_SIMPLES.replace('<state id="0" name="q0">', '<state id="0">')

    automato = converter_jff_para_automato(jff)

    assert any(e.nome == "0" for e in automato.estados)


def test_importar_ler_coordenadas():
    automato = converter_jff_para_automato(JFF_SIMPLES)

    por_nome = {e.nome: e for e in automato.estados}
    assert por_nome["q0"].x == 100.0
    assert por_nome["q0"].y == 200.0
    assert por_nome["q1"].x == 300.0
    assert por_nome["q1"].y == 200.0

