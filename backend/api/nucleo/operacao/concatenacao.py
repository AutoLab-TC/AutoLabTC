"""
Operação de concatenação de autômatos finitos.

A concatenação constrói um AFN que reconhece as cadeias formadas por uma
cadeia aceita pelo primeiro autômato seguida por uma cadeia aceita pelo
segundo. Para isso, os estados finais do primeiro autômato recebem
transições épsilon para o estado inicial do segundo.

A construção segue a ideia apresentada por Michael Sipser em
Introdução à Teoria da Computação: o novo autômato começa no estado inicial
do primeiro, mantém como finais somente os estados finais do segundo e
usa não determinismo para escolher onde termina a parte reconhecida pelo
primeiro autômato.

Formalmente, para os autômatos A1 = (Q1, Σ1, δ1, q1, F1) e
A2 = (Q2, Σ2, δ2, q2, F2), o autômato resultante é:

    Q = Q1 ∪ Q2
    Σ = Σ1 ∪ Σ2
    δ = δ1 ∪ δ2 ∪ {(q, ε, q2) | q ∈ F1}
    estado inicial = q1
    F = F2

Essa é a construção apresentada por Sipser para o fecho das linguagens
regulares sob concatenação (capítulo 1).

Como os estados são identificados pelo nome, um estado do segundo autômato
que tenha o mesmo nome de um estado do primeiro é renomeado com o prefixo
``N2_`` e, se necessário, um sufixo numérico. Assim, os conjuntos de
estados dos dois autômatos permanecem disjuntos.

Cada etapa intermediária é registrada em uma lista de Etapa, contendo
uma descrição textual e uma cópia do autômato naquele momento. Essas
etapas podem ser consumidas posteriormente pelo gerador de PDF.
"""

from api.nucleo.automato_finito import AutomatoFinito
from api.nucleo.dto.etapa import Etapa
from api.nucleo.dto.resultado_operacao import ResultadoOperacao
from api.nucleo.estado import Estado
from api.nucleo.excecoes import OperacaoInvalidaError
from api.nucleo.transicao import Transicao


def _remapear_transicoes(
    transicoes: list[Transicao],
    mapa: dict[Estado, Estado],
) -> list[Transicao]:
    """Recria as transições usando os estados do mapa informado."""
    return [
        Transicao(
            origem=mapa[transicao.origem],
            simbodo=transicao.simbodo,
            destino=mapa[transicao.destino],
        )
        for transicao in transicoes
    ]


def concatenacao(
    automato1: AutomatoFinito, automato2: AutomatoFinito
) -> ResultadoOperacao:
    """
    Calcula a concatenação das linguagens reconhecidas por dois autômatos.

    A operação realiza as seguintes etapas:
        1. Valida e copia os dois autômatos de entrada.
        2. Renomeia os estados do segundo autômato que têm o mesmo nome de
           um estado do primeiro, mantendo os conjuntos de estados disjuntos.
        3. Combina seus estados, alfabetos e transições, mantendo como
           inicial o estado inicial do primeiro e como finais os estados
           finais do segundo.
        4. Adiciona transições épsilon dos estados finais do primeiro
           autômato para o estado inicial do segundo.
        5. Registra as etapas intermediárias e o autômato final.

    A construção não exige que as entradas sejam determinísticas. O
    resultado pode ser um AFN, inclusive quando as entradas já contêm
    transições épsilon.

    Args:
        automato1: Primeiro autômato da concatenação.
        automato2: Segundo autômato da concatenação.

    Returns:
        ResultadoOperacao: Contém o autômato que reconhece a concatenação
        no atributo automato_final e as etapas da operação no atributo
        etapas.

    Raises:
        OperacaoInvalidaError: Se algum dos autômatos de entrada for
        inconsistente ou não possuir um estado inicial válido.
    """
    primeiro = automato1.copiar()
    segundo = automato2.copiar()

    try:
        primeiro.validar()
    except ValueError as erro:
        raise OperacaoInvalidaError(f"O primeiro autômato é inválido: {erro}") from erro

    try:
        segundo.validar()
    except ValueError as erro:
        raise OperacaoInvalidaError(f"O segundo autômato é inválido: {erro}") from erro

    etapas = [
        Etapa(
            descricao="Primeiro autômato de entrada",
            automato=primeiro.copiar(),
        ),
        Etapa(
            descricao="Segundo autômato de entrada",
            automato=segundo.copiar(),
        ),
    ]

    nomes_primeiro = {estado.nome for estado in primeiro.estados}
    nomes_utilizados = nomes_primeiro | {estado.nome for estado in segundo.estados}

    mapa_primeiro: dict[Estado, Estado] = {
        estado: Estado(
            nome=estado.nome,
            inicial=estado == primeiro.estado_inicial,
            final=False,
        )
        for estado in primeiro.estados
    }

    mapa_segundo: dict[Estado, Estado] = {}
    houve_renomeacao = False
    for estado in sorted(segundo.estados, key=lambda item: item.nome):
        nome = estado.nome
        if nome in nomes_primeiro:
            houve_renomeacao = True
            nome_base = f"N2_{nome}"
            nome = nome_base
            sufixo = 1
            while nome in nomes_utilizados:
                nome = f"{nome_base}_{sufixo}"
                sufixo += 1
            nomes_utilizados.add(nome)

        mapa_segundo[estado] = Estado(
            nome=nome,
            inicial=False,
            final=estado in segundo.estados_finais,
        )

    estado_inicial = mapa_primeiro[primeiro.estado_inicial]
    estado_inicial_segundo = mapa_segundo[segundo.estado_inicial]
    estados_finais = {mapa_segundo[estado] for estado in segundo.estados_finais}

    transicoes_primeiro = _remapear_transicoes(primeiro.transicoes, mapa_primeiro)
    transicoes_segundo = _remapear_transicoes(segundo.transicoes, mapa_segundo)

    if houve_renomeacao:
        segundo_renomeado = AutomatoFinito(
            estados=set(mapa_segundo.values()),
            alfabeto=segundo.alfabeto,
            transicoes=list(transicoes_segundo),
            estado_inicial=estado_inicial_segundo,
            estados_finais=set(estados_finais),
        )
        # O snapshot representa o segundo autômato isolado, então o seu
        # estado inicial deve estar marcado como inicial. A cópia evita
        # alterar o estado compartilhado com o autômato combinado, no qual
        # o único estado inicial é o do primeiro autômato.
        snapshot_segundo = segundo_renomeado.copiar()
        if snapshot_segundo.estado_inicial is not None:
            snapshot_segundo.estado_inicial.inicial = True

        etapas.append(
            Etapa(
                descricao=(
                    "Renomear os estados do segundo autômato que têm o mesmo "
                    "nome de um estado do primeiro"
                ),
                automato=snapshot_segundo,
            )
        )

    estados = set(mapa_primeiro.values()) | set(mapa_segundo.values())
    automato_combinado = AutomatoFinito(
        estados=estados,
        alfabeto=primeiro.alfabeto | segundo.alfabeto,
        transicoes=transicoes_primeiro + transicoes_segundo,
        estado_inicial=estado_inicial,
        estados_finais=estados_finais,
    )

    etapas.append(
        Etapa(
            descricao=(
                "Combinar os autômatos mantendo o inicial do primeiro "
                "e os finais do segundo"
            ),
            automato=automato_combinado.copiar(),
        )
    )

    # Ordenar deixa a lista de transições determinística, independente
    # da ordem de iteração do conjunto de estados finais.
    for estado_final in sorted(primeiro.estados_finais, key=lambda estado: estado.nome):
        automato_combinado.adicionar_transicao(
            Transicao(
                origem=mapa_primeiro[estado_final],
                simbodo=None,
                destino=estado_inicial_segundo,
            )
        )

    try:
        automato_combinado.validar()
    except ValueError as erro:
        raise OperacaoInvalidaError(
            f"A concatenação produziu um autômato inválido: {erro}"
        ) from erro

    etapas.append(
        Etapa(
            descricao=(
                "Adicionar transições épsilon dos finais do primeiro "
                "autômato ao inicial do segundo"
            ),
            automato=automato_combinado.copiar(),
        )
    )

    etapas.append(
        Etapa(
            descricao=(
                "Autômato final da concatenação: AFN com transições épsilon, "
                "inicial do primeiro autômato e finais do segundo"
            ),
            automato=automato_combinado.copiar(),
        )
    )

    return ResultadoOperacao(
        automato_final=automato_combinado.copiar(),
        etapas=etapas,
    )
