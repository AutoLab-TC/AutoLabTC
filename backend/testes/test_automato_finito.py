import pytest

from api.nucleo.automato_finito import AutomatoFinito
from api.nucleo.estado import Estado
from api.nucleo.transicao import Transicao


def test_estado_basico():
    e = Estado("q0", inicial=True, final=False)
    assert e.nome == "q0"
    assert e.inicial is True
    assert e.final is False


def test_estado_coordenadas_padrao():
    e = Estado("q0")
    assert e.x == 0.0
    assert e.y == 0.0


def test_estado_coordenadas_informadas():
    e = Estado("q0", x=120.5, y=-30.0)
    assert e.x == 120.5
    assert e.y == -30.0


def test_estado_eq_hash_ignora_coordenadas():
    a = Estado("q0", x=10.0, y=20.0)
    b = Estado("q0", x=99.0, y=99.0)

    assert a == b
    assert hash(a) == hash(b)
    assert len({a, b}) == 1


def test_transicao_normal_e_epsilon():
    q0 = Estado("q0")
    q1 = Estado("q1")
    t1 = Transicao(q0, "a", q1)
    t2 = Transicao(q0, None, q1)  # epsilon
    assert t1.simbodo == "a"
    assert t2.simbodo is None


def test_automato_valido():
    q0 = Estado("q0", inicial=True)
    q1 = Estado("q1", final=True)
    a = AutomatoFinito(
        estados={q0, q1},
        alfabeto={"a"},
        estado_inicial=q0,
        estados_finais={q1},
    )
    a.adicionar_transicao(Transicao(q0, "a", q1))
    a.validar()  # não deve lançar
    assert a.obter_estado_inicial() == q0


def test_validar_estado_inicial_ausente():
    q0 = Estado("q0")
    a = AutomatoFinito(estados={q0}, alfabeto=set(), estado_inicial=None)
    try:
        a.validar()
        assert False, "deveria lançar ValueError"
    except ValueError:
        pass


def test_validar_estado_final_inexistente():
    q0 = Estado("q0", inicial=True)
    q1 = Estado("q1", final=True)
    a = AutomatoFinito(
        estados={q0}, alfabeto=set(), estado_inicial=q0, estados_finais={q1}
    )
    try:
        a.validar()
        assert False, "deveria lançar ValueError"
    except ValueError:
        pass


def test_validar_transicao_estado_desconhecido():
    q0 = Estado("q0", inicial=True)
    q1 = Estado("q1")
    q2 = Estado("q2")
    a = AutomatoFinito(estados={q0, q1}, alfabeto={"a"}, estado_inicial=q0)
    a.adicionar_transicao(Transicao(q0, "a", q2))  # q2 não existe
    try:
        a.validar()
        assert False, "deveria lançar ValueError"
    except ValueError:
        pass


def test_validar_simbodo_fora_do_alfabeto():
    q0 = Estado("q0", inicial=True)
    q1 = Estado("q1")
    a = AutomatoFinito(estados={q0, q1}, alfabeto={"a"}, estado_inicial=q0)
    a.adicionar_transicao(Transicao(q0, "b", q1))  # 'b' não está no alfabeto
    try:
        a.validar()
        assert False, "deveria lançar ValueError"
    except ValueError:
        pass


def construir_automato_organizacao():
    q0 = Estado("q0", inicial=True)
    q1 = Estado("q1")
    q2 = Estado("q2", final=True)
    q3 = Estado("q3")  # inalcançável
    a = AutomatoFinito(
        estados={q0, q1, q2, q3},
        alfabeto={"a", "b"},
        estado_inicial=q0,
        estados_finais={q2},
    )
    a.adicionar_transicao(Transicao(q0, "b", q2))
    a.adicionar_transicao(Transicao(q0, "a", q1))
    a.adicionar_transicao(Transicao(q1, "a", q2))
    return a, q0, q1, q2, q3


def test_organizar_atribui_coordenadas_a_todos():
    a, q0, q1, q2, q3 = construir_automato_organizacao()

    a.organizar()

    posicoes = AutomatoFinito._posicoes_circulares(4)
    atribuidas = [(estado.x, estado.y) for estado in (q0, q1, q2, q3)]
    for coordenada in atribuidas:
        assert coordenada in [pytest.approx(p) for p in posicoes]
    assert len({(q0.x, q0.y), (q1.x, q1.y), (q2.x, q2.y), (q3.x, q3.y)}) == 4


def test_organizar_ordem_busca_largura():
    a, q0, q1, q2, _ = construir_automato_organizacao()

    a.organizar()

    ordem = [q0, q1, q2]  # 'a' antes de 'b', largura a partir de q0
    posicoes = AutomatoFinito._posicoes_circulares(4)
    for estado, esperado in zip(ordem, posicoes):
        assert (estado.x, estado.y) == pytest.approx(esperado)


def test_organizar_inalcancaveis_ao_final():
    a, _, _, _, q3 = construir_automato_organizacao()

    a.organizar()

    posicoes = AutomatoFinito._posicoes_circulares(4)
    assert (q3.x, q3.y) == pytest.approx(posicoes[3])


def test_organizar_deterministico():
    a, *_ = construir_automato_organizacao()
    b, *_ = construir_automato_organizacao()

    a.organizar()
    b.organizar()

    coordenadas_a = sorted((e.nome, e.x, e.y) for e in a.estados)
    coordenadas_b = sorted((e.nome, e.x, e.y) for e in b.estados)
    assert coordenadas_a == coordenadas_b
