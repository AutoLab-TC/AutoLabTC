"""Operação de complemento de autômatos finitos determinísticos (AFD)."""

from api.nucleo.automato_finito import AutomatoFinito
from api.nucleo.dto.resultado_operacao import ResultadoOperacao
from api.nucleo.excecoes import OperacaoInvalidaError
from api.nucleo.dto.etapa import Etapa
from api.nucleo.utilitario.utilitarios_operacoes import completar, inverter_finais

def complemento(automato: AutomatoFinito) -> ResultadoOperacao:
    """Calcula o complemento de um AFD.
    
    Para tal, se faz necessário o cumprimento das seguintes regras:
        1- Ser um AFD.
        2- Estar completo, caso contrário, completa-lo.
    
    Resultado esperado: Inversão dos estados iniciais e finais.

    Args:
        automato: AFD de entrada.

    Returns:
        ResultadoOperacao com o autômato final e as etapas:
        "Autômato original", "Adição de estado sumidouro" (quando
        aplicável) e "Autômato Final".

    Raises:
        OperacaoInvalidaError: se o autômato não for um AFD.
    """

    automato = automato.copiar()

    "Valida se o autômato é um AFD."
    if not automato.eh_afd():
        raise OperacaoInvalidaError(
            "A operação complemento exige um AFD. "
            "O autômato informado é não determinístico; converta-o para AFD antes."
        )

    etapas: list[Etapa] = []

    etapas.append(
        Etapa(
            titulo = "Autômato original",
            descricao = "Autômato de entrada fornecido para a operação.",
            automato = automato.copiar(),
        )
    )

    "Completa o autômato com estados sumidouros, se necessário"
    if not automato.eh_completo():
        completar(automato)
        etapas.append(
            Etapa(
                titulo = "Adição de estado sumidouro",
                descricao = "Completa o autômato com estado sumidouro e transições ausentes.",
                automato = automato.copiar(),
            )
        )

    "Inverte os estados finais e registra as etapas."
    inverter_finais(automato)
    etapas.append(
        Etapa(
            titulo = "Autômato Final",
            descricao = "Resultado da operação após a inversão dos estados finais.",
            automato = automato.copiar(),
        )
    )

    return ResultadoOperacao(
        titulo = "Complemento de AFD",
        automato_final = automato.copiar(),
        etapas = etapas,
    )