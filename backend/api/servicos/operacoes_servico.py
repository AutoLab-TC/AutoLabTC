from api.nucleo.dto.resposta_operacao import RespostaOperacao
from api.nucleo.operacao.complemento import complemento as complemento_afd
from api.nucleo.utilitario.utilitarios_jff import (
    converter_alfabeto_json,
    converter_automato_para_jff,
    converter_jff_para_automato,
)
from api.relatorios.documento import gerar_pdf


def complemento(
    jff_bytes: bytes,
    alfabeto: str | None = None,
) -> RespostaOperacao:
    """Realiza a operação de complemento e gera os arquivos de resposta.

    Converte o .jff recebido em um AutomatoFinito, calcula o complemento
    e produz o .jff do autômato resultante e o relatório PDF com as
    etapas intermediárias da operação.

    Se ``alfabeto`` for informado, deve ser uma string JSON (ex: ["a","b","c"])
    que substitui o alfabeto derivado do .jff.

    Raises:
        ErroJFFInvalido: se o conteúdo não for um .jff válido, ou se o
            alfabeto informado não contiver todos os símbolos usados.
        OperacaoInvalidaError: se o autômato não for um AFD.
        ErroGeracaoPdf: se o relatório PDF não puder ser gerado.
    """
    jff = jff_bytes.decode("utf-8")

    alfabeto_final = converter_alfabeto_json(alfabeto) if alfabeto else None

    automato = converter_jff_para_automato(jff, alfabeto=alfabeto_final)
    resultado = complemento_afd(automato)

    return RespostaOperacao(
        arquivo_jff=converter_automato_para_jff(resultado.automato_final),
        relatorio_pdf=gerar_pdf(resultado, titulo="Complemento"),
    )
