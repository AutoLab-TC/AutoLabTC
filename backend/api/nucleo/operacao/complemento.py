"""Operação de complemento de autômatos finitos determinísticos (AFD)."""

from api.nucleo.automato_finito import AutomatoFinito
from api.nucleo.dto.resultado_operacao import ResultadoOperacao
from api.nucleo.excecoes import OperacaoInvalidaError
from api.nucleo.dto.etapa import Etapa
from api.nucleo.utilitario.utilitarios_operacoes import completar, inverter_finais

REF_AFD = "Sipser, Cap. 1, p. 32 (definição formal de AFD)"
REF_AFN_PARA_AFD = "Sipser, Teorema 1.19, p. 46"


def complemento(automato: AutomatoFinito) -> ResultadoOperacao:
    """Calcula o complemento de um AFD.

    O complemento reconhece exatamente as palavras que o autômato
    original rejeita.

    Requisitos:
        1- Ser um AFD.
        2- Estar completo; caso contrário, completá-lo com um
           estado poço.

    Resultado esperado: os estados finais são invertidos. Estado
    inicial, alfabeto e transições originais não mudam.

    Args:
        automato: AFD de entrada.

    Returns:
        ResultadoOperacao com o autômato final e as etapas:
        "Autômato original", "Adição de estado poço" (quando
        aplicável) e "Inversão dos estados finais".

    Raises:
        OperacaoInvalidaError: se o autômato não for um AFD.
    """

    automato = automato.copiar()

    if not automato.eh_afd():
        raise OperacaoInvalidaError(
            "A operação complemento exige um AFD. "
            "O autômato informado é não determinístico; "
            f"converta-o para AFD antes ({REF_AFN_PARA_AFD})."
        )

    etapas: list[Etapa] = []

    etapas.append(
        Etapa(
            titulo = "Autômato original",
            descricao = (
                "Este é o AFD de entrada. Queremos construir outro AFD que "
                "aceite exatamente as palavras que este rejeita.\n"
                "Isso só funciona com AFD, pois nele cada palavra termina em "
                "um único estado.\n"
                f"Referência: {REF_AFD}."
            ),
            automato = automato.copiar(),
        )
    )

    foi_completado = not automato.eh_completo()
    if foi_completado:
        completar(automato)
        etapas.append(
            Etapa(
                titulo = "Adição de estado poço",
                descricao = (
                    "Faltavam transições. Em um AFD completo, todo estado "
                    "tem uma transição para cada símbolo do alfabeto.\n"
                    "Foi criado um estado poço (não final) que aponta "
                    "para si mesmo, e as transições ausentes foram "
                    "direcionadas a ele. A linguagem não muda."
                ),
                automato = automato.copiar(),
            )
        )

    inverter_finais(automato)

    if foi_completado:
        trecho_inversao = (
            "Estados finais viraram não finais, e os não finais "
            "(incluindo o estado poço) viraram finais. Todo o resto "
            "permanece igual.\n"
        )
    else:
        trecho_inversao = (
            "Estados finais viraram não finais, e os não finais "
            "viraram finais. Todo o resto permanece igual.\n"
        )

    etapas.append(
        Etapa(
            titulo = "Inversão dos estados finais",
            descricao = (
                trecho_inversao
                + "Como cada palavra termina em um único estado, o que era "
                "aceito agora é rejeitado, e vice-versa."
            ),
            automato = automato.copiar(),
        )
    )

    return ResultadoOperacao(
        automato_final = automato.copiar(),
        etapas = etapas,
    )