"""Conversão de um autômato finito para um diagrama TikZ."""

from api.nucleo.automato_finito import AutomatoFinito
from api.nucleo.estado import Estado
from api.relatorios.latex import escapar_latex


def automato_para_tikz(automato: AutomatoFinito) -> str:
    """Gera o código TikZ que desenha um autômato finito.

    Cada estado é desenhado nas coordenadas x/y armazenadas nele; chame
    ``AutomatoFinito.organizar()`` antes para garantir um layout
    organizado. Transições entre o mesmo par de estados são agrupadas em
    uma única aresta, com os símbolos separados por vírgula.
    Autotransições usam ``loop`` e arestas de ida e volta recebem uma
    curvatura para não se sobreporem.
    """
    automato.validar()

    estados = sorted(automato.estados, key=lambda estado: estado.nome)
    ids = {estado: f"q{indice}" for indice, estado in enumerate(estados)}
    indices = {estado: indice for indice, estado in enumerate(estados)}

    linhas = [r"\begin{tikzpicture}[shorten >=1pt,node distance=2.8cm,on grid,auto]"]

    for estado in estados:
        estilos = ["state"]
        if estado == automato.estado_inicial:
            estilos.append("initial")
        if estado in automato.estados_finais:
            estilos.append("accepting")

        linhas.append(
            f"  \\node[{', '.join(estilos)}] ({ids[estado]}) "
            f"at ({estado.x:.1f},{estado.y:.1f}) {{{escapar_latex(estado.nome)}}};"
        )

    transicoes = _agrupar_por_par(automato)
    arestas = sorted(
        transicoes.items(),
        key=lambda item: (indices[item[0][0]], indices[item[0][1]]),
    )

    if arestas:
        linhas.append(r"  \path[->]")
        comandos = []
        for (origem, destino), simbolos in arestas:
            rotulo = _rotulo_simbolos(simbolos)

            if origem == destino:
                direcao = "loop above" if origem.y >= 0 else "loop below"
                comandos.append(
                    f"    ({ids[origem]}) edge [{direcao}] "
                    f"node {{{rotulo}}} ({ids[destino]})"
                )
                continue

            opcao = ""
            if (destino, origem) in transicoes:
                opcao = " [bend left=25]"

            comandos.append(
                f"    ({ids[origem]}) edge{opcao} "
                f"node {{{rotulo}}} ({ids[destino]})"
            )

        linhas.append("\n".join(comandos) + ";")

    linhas.append(r"\end{tikzpicture}")
    return "\n".join(linhas)


def _agrupar_por_par(
    automato: AutomatoFinito,
) -> dict[tuple[Estado, Estado], list[str | None]]:
    """Agrupa os símbolos das transições por par de origem e destino."""
    grupos: dict[tuple[Estado, Estado], list[str | None]] = {}

    for transicao in sorted(
        automato.transicoes,
        key=lambda transicao: (
            transicao.origem.nome,
            transicao.destino.nome,
            transicao.simbodo is not None,
            transicao.simbodo or "",
        ),
    ):
        simbolos = grupos.setdefault((transicao.origem, transicao.destino), [])
        if transicao.simbodo not in simbolos:
            simbolos.append(transicao.simbodo)

    return grupos


def _rotulo_simbolos(simbolos: list[str | None]) -> str:
    """Monta o rótulo LaTeX de uma aresta."""
    rotulos = [
        r"\varepsilon" if simbolo is None else escapar_latex(simbolo)
        for simbolo in simbolos
    ]
    return ", ".join(rotulos)
