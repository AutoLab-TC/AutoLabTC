from api.nucleo.dto.resposta_operacao import RespostaOperacao
from api.nucleo.operacao.complemento import complemento as complemento_afd
from api.nucleo.operacao.concatenacao import concatenacao as concatenacao_afd
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
    """Realiza o complemento de um AFD e gera o .jff e o PDF das etapas."""
    jff = jff_bytes.decode("utf-8")

    alfabeto_final = converter_alfabeto_json(alfabeto) if alfabeto else None

    automato = converter_jff_para_automato(jff, alfabeto=alfabeto_final)
    resultado = complemento_afd(automato)

    resultado.automato_final.organizar()

    return RespostaOperacao(
        arquivo_jff=converter_automato_para_jff(resultado.automato_final),
        relatorio_pdf=gerar_pdf(resultado, titulo="Complemento"),
    )


def concatenacao(
    jff1_bytes: bytes,
    jff2_bytes: bytes,
    alfabeto1: str | None = None,
    alfabeto2: str | None = None,
) -> RespostaOperacao:
    """Realiza a concatenação de dois autômatos e gera o .jff e o PDF das etapas."""
    jff1 = jff1_bytes.decode("utf-8")
    jff2 = jff2_bytes.decode("utf-8")

    alfabeto1_final = converter_alfabeto_json(alfabeto1) if alfabeto1 else None
    alfabeto2_final = converter_alfabeto_json(alfabeto2) if alfabeto2 else None

    automato1 = converter_jff_para_automato(jff1, alfabeto=alfabeto1_final)
    automato2 = converter_jff_para_automato(jff2, alfabeto=alfabeto2_final)
    resultado = concatenacao_afd(automato1, automato2)

    resultado.automato_final.organizar()

    return RespostaOperacao(
        arquivo_jff=converter_automato_para_jff(resultado.automato_final),
        relatorio_pdf=gerar_pdf(resultado, titulo="Concatenação"),
    )
