"""Operação de concatenação de autômatos finitos."""

from api.nucleo.automato_finito import AutomatoFinito
from api.nucleo.dto.etapa import Etapa
from api.nucleo.dto.resultado_operacao import ResultadoOperacao
from api.nucleo.estado import Estado
from api.nucleo.excecoes import OperacaoInvalidaError
from api.nucleo.transicao import Transicao

REF_CONCATENACAO = "Sipser, Teorema 1.23, p. 52"


def _copiar_com_prefixo(automato: AutomatoFinito, prefixo: str) -> AutomatoFinito:
    """Copia o autômato renomeando seus estados com o prefixo dado."""
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
    """Concatena as linguagens de dois autômatos, retornando o AFN resultante e suas etapas."""
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
                "Este é o autômato N1, que reconhece A1: ele aceita a "
                "primeira parte da palavra.\n"
                "Seus estados ganharam o prefixo A1 para não se misturarem "
                "com os de N2 quando os dois forem unidos.\n"
                "O estado inicial continua sendo q1 e os estados finais, F1.\n"
                f"Referência: {REF_CONCATENACAO}."
            ),
            automato=primeiro.copiar(),
        ),
        Etapa(
            titulo="Segundo autômato de entrada",
            descricao=(
                "Este é o autômato N2, que reconhece A2: ele aceita a "
                "segunda parte da palavra.\n"
                "Seus estados ganharam o prefixo A2, ficando separados dos "
                "estados de N1.\n"
                "O estado inicial continua sendo q2 e os estados finais, F2."
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
            titulo="União dos autômatos",
            descricao=(
                "Primeiro passo da prova do Teorema 1.23: juntamos N1 e N2 "
                "em um único autômato.\n"
                "Os estados, o alfabeto e as transições são a união dos "
                "dois autômatos.\n"
                "O estado inicial é q1 (o de N1) e os únicos estados finais "
                "são F2 (os de N2).\n"
                "Falta ainda ligar os dois: sem as setas épsilon, ele ainda "
                "não reconhece A1 concatenado com A2."
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
            titulo="Transições épsilon entre N1 e N2",
            descricao=(
                "Agora ligamos os dois autômatos: para cada estado final de "
                "N1, criamos uma seta épsilon até o inicial q2 de N2.\n"
                "Épsilon não consome nenhum símbolo — ela deixa o autômato "
                "'adivinhar' onde termina a primeira parte.\n"
                "Ao chegar em um estado final de N1, ele pode seguir para "
                "N2 sem ler mais nada."
            ),
            automato=automato_combinado.copiar(),
        )
    )

    etapas.append(
        Etapa(
            titulo="Autômato final da concatenação",
            descricao=(
                "Este é o autômato N do Teorema 1.23: começa em q1, termina "
                "em um estado de F2 e já tem as setas épsilon.\n"
                "Ele aceita a palavra quando dá para dividi-la em duas "
                "partes — a primeira aceita por N1 e a segunda por N2.\n"
                "O não determinismo é justamente o que permite adivinhar "
                "onde fazer essa divisão."
            ),
            automato=automato_combinado.copiar(),
        )
    )

    return ResultadoOperacao(
        automato_final=automato_combinado.copiar(),
        etapas=etapas,
    )
