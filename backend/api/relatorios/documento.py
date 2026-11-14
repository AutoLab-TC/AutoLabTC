"""Geração do relatório PDF com as etapas de uma operação."""

import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from pylatex import Center, Command, Document, NoEscape, Section
from pylatex.headfoot import Foot, Head, PageStyle
from pylatex.package import Package

from api.nucleo.dto.resultado_operacao import ResultadoOperacao
from api.nucleo.excecoes import ErroGeracaoPdf
from api.relatorios.diagrama import automato_para_tikz
from api.relatorios.latex import escapar_latex


def gerar_pdf(
    resultado: ResultadoOperacao,
    titulo: str | None = None,
    cabecalho: str | None = None,
) -> bytes:
    """Gera um PDF com o diagrama de cada etapa da operação.

    O compilador ``pdflatex`` precisa estar disponível no ``PATH`` do
    processo. O documento é criado em um diretório temporário e o conteúdo
    binário do PDF é retornado; o código LaTeX não é exposto pela API.

    Raises:
        ErroGeracaoPdf: se o LaTeX não estiver disponível ou se a compilação
            falhar.
    """

    "Faz com que cada operação precise definir seu titulo e cabeçalho"
    if titulo is None:
        titulo = getattr(resultado, "titulo", None)
    if cabecalho is None:
        cabecalho = getattr(resultado, "cabecalho", None)
    if cabecalho is None:
        cabecalho = titulo
    if titulo is None:
        titulo = cabecalho
    if titulo is None:
        titulo = "Operação"
    if cabecalho is None:
        cabecalho = titulo

    if shutil.which("pdflatex") is None:
        raise ErroGeracaoPdf(
            "O compilador LaTeX (pdflatex) não está disponível no servidor."
        )

    try:
        return _gerar_pdf(resultado, titulo, cabecalho)
    except ErroGeracaoPdf:
        raise
    except Exception as erro:
        raise ErroGeracaoPdf("Não foi possível gerar o PDF do relatório.") from erro


def _gerar_pdf(resultado: ResultadoOperacao, titulo: str, cabecalho: str) -> bytes:
    titulo_escaped = escapar_latex(titulo)
    cabecalho_escaped = escapar_latex(cabecalho)

    documento = Document(documentclass="article", page_numbers=False)
    documento.change_document_style("plain")
    documento.preamble.append(NoEscape(r"\usepackage{tikz}"))
    documento.preamble.append(NoEscape(r"\usetikzlibrary{automata,positioning}"))
    documento.preamble.append(Package("fancyhdr"))

    estilo = PageStyle("autolab", header_thickness=0.4, footer_thickness=0.4)
    estilo.append(Head("L", data=NoEscape(escapar_latex("AutoLab-TC"))))
    estilo.append(Head("R", data=NoEscape(cabecalho_escaped)))
    estilo.append(
        Foot(
            "L",
            data=NoEscape(
                r"\small "
                + escapar_latex(
                    "SIPSER, Michael. Introdução à teoria da computação. "
                    "Tradução de Ruy José Guerra Barretto de Queiroz; "
                    "revisão de Newton José Vieira. São Paulo: Thomson Learning, "
                    "2007. 459 p. ISBN 9788522104994"
                )
            ),
        )
    )
    estilo.append(Foot("R", data=NoEscape(r"\small Página \thepage")))
    documento.preamble.append(estilo)

    documento.preamble.append(NoEscape(r"\title{" + titulo_escaped + "}"))
    documento.preamble.append(Command("date", ""))

    documento.append(NoEscape(r"\maketitle"))
    documento.append(NoEscape(r"\thispagestyle{autolab}"))
    documento.change_document_style("autolab")

    documento.append(Section("Resumo", numbering=False, label=False))
    documento.append(NoEscape(escapar_latex(f"Operação: {titulo}.")))
    documento.append(NoEscape(r"\par\noindent"))
    documento.append(NoEscape(escapar_latex(f"Total de etapas: {len(resultado.etapas)}.")))
    documento.append(NoEscape(r"\par\bigskip"))

    for indice, etapa in enumerate(resultado.etapas, start=1):
        documento.append(
            Section(
                NoEscape(f"Etapa {indice} - {escapar_latex(etapa.titulo)}"),
                numbering=False,
                label=False,
            )
        )
        if etapa.descricao:
            documento.append(NoEscape(escapar_latex(etapa.descricao)))
            documento.append(NoEscape(r"\par"))
        centro = Center()
        centro.append(NoEscape(automato_para_tikz(etapa.automato)))
        documento.append(centro)
        documento.append(NoEscape(r"\par\bigskip"))

    documento.append(NoEscape(r"Documento gerado automaticamente pelo AutoLab-TC."))

    with TemporaryDirectory(prefix="autolab_pdf_") as diretorio:
        caminho_base = Path(diretorio) / "complemento"
        documento.generate_pdf(
            str(caminho_base),
            clean=True,
            clean_tex=True,
            compiler="pdflatex",
            compiler_args=["-halt-on-error"],
        )

        caminho_pdf = caminho_base.with_suffix(".pdf")
        if not caminho_pdf.exists() or caminho_pdf.stat().st_size == 0:
            raise ErroGeracaoPdf("O compilador LaTeX não produziu um PDF.")

        return caminho_pdf.read_bytes()
