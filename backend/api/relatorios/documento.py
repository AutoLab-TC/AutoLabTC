"""Geração do relatório PDF com as etapas de uma operação."""

import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from pylatex import Center, Document, NoEscape, Section
from pylatex.headfoot import Foot, Head, PageStyle
from pylatex.package import Package

from api.nucleo.dto.resultado_operacao import ResultadoOperacao
from api.nucleo.excecoes import ErroGeracaoPdf
from api.relatorios.diagrama import automato_para_tikz
from api.relatorios.latex import escapar_latex


def gerar_pdf(
    resultado: ResultadoOperacao,
    titulo: str,
) -> bytes:
    """Gera um PDF com o diagrama de cada etapa da operação.

    A primeira página contém o nome AutoLab-TC no topo, o título da
    operação centralizado e o resumo; cada etapa ocupa uma página própria.
    O rodapé traz a referência do livro do Sipser em todas as páginas.

    O compilador ``pdflatex`` precisa estar disponível no ``PATH`` do
    processo. O documento é criado em um diretório temporário e o conteúdo
    binário do PDF é retornado; o código LaTeX não é exposto pela API.

    Raises:
        ErroGeracaoPdf: se o LaTeX não estiver disponível ou se a compilação
            falhar.
    """

    if shutil.which("pdflatex") is None:
        raise ErroGeracaoPdf(
            "O compilador LaTeX (pdflatex) não está disponível no servidor."
        )

    try:
        return _gerar_pdf(resultado, titulo)
    except ErroGeracaoPdf:
        raise
    except Exception as erro:
        raise ErroGeracaoPdf("Não foi possível gerar o PDF do relatório.") from erro


def _gerar_pdf(resultado: ResultadoOperacao, titulo: str) -> bytes:
    titulo_escaped = escapar_latex(f"Operação: {titulo}")

    documento = Document(documentclass="article", page_numbers=False)
    documento.preamble.append(NoEscape(r"\usepackage[margin=2cm]{geometry}"))
    documento.preamble.append(NoEscape(r"\usepackage{tikz}"))
    documento.preamble.append(NoEscape(r"\usetikzlibrary{automata,positioning}"))
    documento.preamble.append(Package("fancyhdr"))

    estilo_capa = PageStyle("autolabcapa", header_thickness=0.4)
    estilo = PageStyle("autolab", header_thickness=0.4, footer_thickness=0.4)

    estilo_capa.append(
        Head("C", data=NoEscape(r"\large " + escapar_latex("AutoLab-TC")))
    )

    estilo.append(
        Head(
            "C",
            data=NoEscape(
                r"\small "
                + escapar_latex("Documento gerado automaticamente pelo AutoLab-TC")
            ),
        )
    )
    estilo.append(
        Foot(
            "L",
            data=NoEscape(
                r"\footnotesize \parbox{0.9\textwidth}{"
                + escapar_latex(
                    "SIPSER, Michael. Introdução à teoria da computação. "
                    "Tradução de Ruy José Guerra Barretto de Queiroz; "
                    "revisão de Newton José Vieira. São Paulo: Thomson Learning, "
                    "2007. 459 p. ISBN 9788522104994"
                )
                + "}"
            ),
        )
    )
    estilo.append(Foot("R", data=NoEscape(r"\small \thepage")))

    documento.preamble.append(estilo_capa)
    documento.preamble.append(estilo)
    documento.change_document_style("autolab")

    documento.append(NoEscape(r"\thispagestyle{autolabcapa}"))
    documento.append(NoEscape(r"\vspace*{\fill}"))
    documento.append(NoEscape(r"\begin{center}"))
    documento.append(NoEscape(r"\fontsize{36}{43.2}\selectfont " + titulo_escaped))
    documento.append(NoEscape(r"\end{center}"))
    documento.append(NoEscape(r"\vspace*{\fill}"))

    documento.append(NoEscape(r"\begin{center}"))
    documento.append(
        NoEscape(
            r"\textbf{\Large "
            + escapar_latex(f"Total de etapas: {len(resultado.etapas)}")
            + "}"
        )
    )
    documento.append(NoEscape(r"\end{center}"))
    documento.append(NoEscape(r"\newpage"))
    documento.append(NoEscape(r"\setcounter{page}{1}"))

    for indice, etapa in enumerate(resultado.etapas, start=1):
        documento.append(
            Section(
                NoEscape(
                    r"\fontsize{16}{19.5}\selectfont "
                    f"Etapa {indice} - {escapar_latex(etapa.titulo)}"
                ),
                numbering=False,
                label=False,
            )
        )
        if etapa.descricao:
            documento.append(
                NoEscape(r"{\large " + escapar_latex(etapa.descricao) + "}")
            )
            documento.append(NoEscape(r"\par"))
        documento.append(NoEscape(r"\vspace*{\fill}"))
        centro = Center()
        centro.append(NoEscape(automato_para_tikz(etapa.automato)))
        documento.append(centro)
        documento.append(NoEscape(r"\vspace*{\fill}"))
        if indice < len(resultado.etapas):
            documento.append(NoEscape(r"\newpage"))

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
