"""
Operação de concatenação de autômatos finitos.

A concatenação constrói um AFN que reconhece as cadeias formadas por uma
cadeia aceita pelo primeiro autômato seguida por uma cadeia aceita pelo
segundo. Para isso, os estados finais do primeiro autômato recebem
transições épsilon para o estado inicial do segundo.

A construção segue a prova apresentada por Michael Sipser em Introdução à
Teoria da Computação (Teorema 1.47, p. 61): o novo autômato começa no
estado inicial do primeiro, mantém como finais somente os estados finais do
segundo e usa o não determinismo para escolher onde termina a parte
reconhecida pelo primeiro autômato.

Formalmente, para os autômatos A1 = (Q1, Σ1, δ1, q1, F1) e
A2 = (Q2, Σ2, δ2, q2, F2), o autômato resultante é:

    Q = Q1 ∪ Q2
    Σ = Σ1 ∪ Σ2
    δ = δ1 ∪ δ2 ∪ {(q, ε, q2) | q ∈ F1}
    estado inicial = q1
    F = F2

Para que a união Q = Q1 ∪ Q2 seja feita sem ambiguidade, os estados são
renomeados no momento da cópia: os estados do primeiro autômato recebem o
prefixo ``A1_`` e os do segundo o prefixo ``A2_``. Como os prefixos são
diferentes, os dois conjuntos de estados ficam sempre disjuntos, sem
precisar comparar nomes.

Cada etapa intermediária é registrada em uma lista de Etapa, com título,
descrição e uma cópia do autômato naquele momento. Essas etapas são
consumidas pelo gerador de PDF.
"""

from api.nucleo.automato_finito import AutomatoFinito
from api.nucleo.dto.etapa import Etapa
from api.nucleo.dto.resultado_operacao import ResultadoOperacao
from api.nucleo.estado import Estado
from api.nucleo.excecoes import OperacaoInvalidaError
from api.nucleo.transicao import Transicao

REF_CONCATENACAO = "Sipser, Teorema 1.47, p. 61"


def _copiar_com_prefixo(automato: AutomatoFinito, prefixo: str) -> AutomatoFinito:
    """Cria uma cópia do autômato renomeando cada estado com o prefixo.

    A renomeação acontece junto com a cópia, antes de qualquer outra
    operação, e garante que os conjuntos de estados de autômatos
    diferentes sejam sempre disjuntos. Os estados e as transições do
    autômato devolvido são objetos novos; por isso o autômato de entrada
    nunca é alterado, mesmo sem uma cópia profunda prévia. Como as
    transições já apontam para os estados renomeados, não é preciso
    remapeá-las depois.
    """
    renomeados: dict[Estado, Estado] = {
        estado: Estado(
            nome=f"{prefixo}_{estado.nome}",
            inicial=estado.inicial,
            final=estado.final,
            x=estado.x,
            y=estado.y,
        )
        for estado in automato.estados
    }
    return AutomatoFinito(
        estados=set(renomeados.values()),
        alfabeto=set(automato.alfabeto),
        transicoes=[
            Transicao(
                origem=renomeados[transicao.origem],
                simbolo=transicao.simbolo,
                destino=renomeados[transicao.destino],
            )
            for transicao in automato.transicoes
        ],
        estado_inicial=renomeados[automato.estado_inicial],
        estados_finais={renomeados[estado] for estado in automato.estados_finais},
    )


def concatenacao(
    automato1: AutomatoFinito, automato2: AutomatoFinito
) -> ResultadoOperacao:
    """
    Calcula a concatenação das linguagens reconhecidas por dois autômatos.

    A operação realiza as seguintes etapas:
        1. Valida os dois autômatos de entrada.
        2. Copia os autômatos renomeando os estados com os prefixos A1 e
           A2, o que mantém os conjuntos de estados disjuntos.
        3. Combina estados, alfabetos e transições, mantendo como inicial
           o estado inicial do primeiro e como finais os estados finais do
           segundo (itens 1 a 3 da prova do Teorema 1.47 de Sipser).
        4. Adiciona transições épsilon dos estados finais do primeiro
           autômato para o estado inicial do segundo (item 4 da prova).
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
    try:
        automato1.validar()
    except ValueError as erro:
        raise OperacaoInvalidaError(f"O primeiro autômato é inválido: {erro}") from erro

    try:
        automato2.validar()
    except ValueError as erro:
        raise OperacaoInvalidaError(f"O segundo autômato é inválido: {erro}") from erro

    primeiro = _copiar_com_prefixo(automato1, "A1")
    segundo = _copiar_com_prefixo(automato2, "A2")

    etapas = [
        Etapa(
            titulo="Primeiro autômato de entrada",
            descricao=(
                "Este é o primeiro autômato da concatenação, o N1 do "
                "Sipser, que reconhece a linguagem A1.\n"
                "Os estados são copiados com o prefixo A1, o que mantém Q1 "
                "e Q2 disjuntos para a união de Q1 com Q2.\n"
                "O estado inicial q1 e os estados finais F1 permanecem os "
                "mesmos.\n"
                f"Referência: {REF_CONCATENACAO}."
            ),
            automato=primeiro.copiar(),
        ),
        Etapa(
            titulo="Segundo autômato de entrada",
            descricao=(
                "Este é o segundo autômato, o N2 do Sipser, que reconhece "
                "a linguagem A2.\n"
                "Os estados são copiados com o prefixo A2, então nenhum "
                "estado de N1 se confunde com um estado de N2.\n"
                "O estado inicial q2 e os estados finais F2 são "
                "preservados."
            ),
            automato=segundo.copiar(),
        ),
    ]

    estado_inicial = primeiro.estado_inicial
    estado_inicial_segundo = segundo.estado_inicial
    estados_finais = set(segundo.estados_finais)

    automato_combinado = AutomatoFinito(
        estados=primeiro.estados | segundo.estados,
        alfabeto=primeiro.alfabeto | segundo.alfabeto,
        transicoes=primeiro.transicoes + segundo.transicoes,
        estado_inicial=estado_inicial,
        estados_finais=estados_finais,
    )

    # O combinado reúne os estados de N1 e de N2, mas só pode ter um estado
    # inicial (o de N1) e como finais apenas os de N2 (F = F2). Normalizar
    # os atributos mantém cada Estado coerente com os campos
    # estado_inicial e estados_finais do autômato, inclusive para as
    # etapas seguintes e para quem consumir o resultado.
    for estado in automato_combinado.estados:
        estado.inicial = estado == estado_inicial
        estado.final = estado in estados_finais

    etapas.append(
        Etapa(
            titulo=(
                "Combinar os autômatos mantendo o inicial do primeiro "
                "e os finais do segundo"
            ),
            descricao=(
                "Primeira parte da prova do Teorema 1.47 (itens 1 a 3).\n"
                "O conjunto de estados é a união de Q1 com Q2, o alfabeto "
                "é a união dos dois alfabetos e a função de transição "
                "reúne as transições de N1 e de N2.\n"
                "O estado inicial é q1, o mesmo de N1, e os únicos estados "
                "finais são os de F2, os finais de N2.\n"
                "Ainda não existem transições épsilon, então o autômato "
                "ainda não reconhece A1 concatenado com A2."
            ),
            automato=automato_combinado.copiar(),
        )
    )

    # Ordenar deixa a lista de transições determinística, independente
    # da ordem de iteração do conjunto de estados finais.
    for estado_final in sorted(primeiro.estados_finais, key=lambda estado: estado.nome):
        automato_combinado.adicionar_transicao(
            Transicao(
                origem=estado_final,
                simbolo=None,
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
            titulo=(
                "Adicionar transições épsilon dos finais do primeiro "
                "autômato ao inicial do segundo"
            ),
            descricao=(
                "Item 4 da prova do Teorema 1.47.\n"
                "Para cada estado final de N1 é criada uma transição "
                "épsilon até o estado inicial q2 de N2.\n"
                "Épsilon não consome símbolo: ela permite saltar de N1 "
                "para N2 no ponto em que N1 termina de reconhecer um "
                "prefixo da entrada.\n"
                "A função de transição passa a ser a de N1 unida à de N2, "
                "acrescida dessas transições épsilon."
            ),
            automato=automato_combinado.copiar(),
        )
    )

    etapas.append(
        Etapa(
            titulo=(
                "Autômato final da concatenação: AFN com transições "
                "épsilon, inicial do primeiro autômato e finais do segundo"
            ),
            descricao=(
                "Este é o autômato N do Teorema 1.47, com estados Q, "
                "estado inicial q1 e estados finais F2.\n"
                "O não determinismo permite adivinhar onde a entrada deve "
                "ser dividida: a palavra é aceita quando pode ser separada "
                "em duas partes, a primeira aceita por N1 e a segunda por "
                "N2.\n"
                "Como apenas os estados finais de N2 continuam finais, a "
                "segunda parte precisa ser lida por N2 até um de seus "
                "estados finais."
            ),
            automato=automato_combinado.copiar(),
        )
    )

    return ResultadoOperacao(
        automato_final=automato_combinado.copiar(),
        etapas=etapas,
    )
