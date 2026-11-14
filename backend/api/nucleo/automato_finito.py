import copy
import math
from dataclasses import dataclass, field

from api.nucleo.estado import Estado
from api.nucleo.transicao import Transicao


@dataclass
class AutomatoFinito:
    """Agrega estados, alfabeto, transições e estados inicial/finais de um autômato."""

    _RAIO_MINIMO = 2.0
    _ESPACO_POR_ESTADO = 3.2

    estados: set[Estado] = field(default_factory=set)
    alfabeto: set[str] = field(default_factory=set)
    transicoes: list[Transicao] = field(default_factory=list)
    estado_inicial: Estado | None = None
    estados_finais: set[Estado] = field(default_factory=set)

    def adicionar_estado(self, estado: Estado) -> None:
        self.estados.add(estado)

    def adicionar_transicao(self, transicao: Transicao) -> None:
        self.transicoes.append(transicao)

    def obter_estado_inicial(self) -> Estado | None:
        return self.estado_inicial

    def organizar(self) -> None:
        """Atribui coordenadas x/y a todos os estados, de forma determinística.

        Os estados são ordenados pela descoberta em largura a partir do
        estado inicial (estados inalcançáveis ao final, em ordem de nome) e
        distribuídos em um círculo, começando pelo topo. As coordenadas
        ficam armazenadas nos próprios estados e são consumidas tanto pela
        serialização .jff quanto pelo diagrama TikZ do relatório.
        """
        ordem = self._ordenar_estados()
        posicoes = self._posicoes_circulares(len(ordem))

        for estado, (x, y) in zip(ordem, posicoes):
            estado.x = x
            estado.y = y

    def _ordenar_estados(self) -> list[Estado]:
        """Ordena os estados pela descoberta em largura a partir do inicial.

        A ordem de descoberta deixa estados adjacentes próximos no círculo e
        garante que estados inalcançáveis apareçam ao final, em ordem de nome.
        """
        ordem: list[Estado] = []
        visitados: set[Estado] = set()
        fila: list[Estado] = [self.estado_inicial]

        while fila:
            estado = fila.pop(0)
            if estado in visitados:
                continue

            visitados.add(estado)
            ordem.append(estado)
            for transicao in sorted(
                self.transicoes,
                key=lambda transicao: (
                    transicao.simbodo is not None,
                    transicao.simbodo or "",
                    transicao.destino.nome,
                ),
            ):
                if transicao.origem == estado and transicao.destino not in visitados:
                    fila.append(transicao.destino)

        for estado in sorted(self.estados, key=lambda estado: estado.nome):
            if estado not in visitados:
                ordem.append(estado)

        return ordem

    @staticmethod
    def _posicoes_circulares(quantidade: int) -> list[tuple[float, float]]:
        """Distribui os estados em um círculo, começando pelo topo."""
        if quantidade == 1:
            return [(0.0, 0.0)]
        if quantidade == 2:
            return [
                (-AutomatoFinito._RAIO_MINIMO, 0.0),
                (AutomatoFinito._RAIO_MINIMO, 0.0),
            ]

        raio = max(
            AutomatoFinito._RAIO_MINIMO,
            quantidade * AutomatoFinito._ESPACO_POR_ESTADO / (2 * math.pi),
        )
        posicoes = []
        for indice in range(quantidade):
            angulo = math.radians(90 - 360 * indice / quantidade)
            posicoes.append((raio * math.cos(angulo), raio * math.sin(angulo)))
        return posicoes

    def validar(self) -> None:
        """Verifica a consistência do autômato; lança ValueError se inválido."""
        if self.estado_inicial is None or self.estado_inicial not in self.estados:
            raise ValueError(
                "Estado inicial ausente ou inexistente no conjunto de estados."
            )
        if not self.estados_finais.issubset(self.estados):
            raise ValueError(
                "Existem estados finais que não pertencem ao conjunto de estados."
            )
        for t in self.transicoes:
            if t.origem not in self.estados or t.destino not in self.estados:
                raise ValueError("Transição referencia estado inexistente.")
            if t.simbodo is not None and t.simbodo not in self.alfabeto:
                raise ValueError(f"Símbodo '{t.simbodo}' não pertence ao alfabeto.")

    def copiar(self) -> "AutomatoFinito":
        """Retorna uma cópia profunda do autômato."""
        return copy.deepcopy(self)

    def eh_afd(self) -> bool:
        """Verifica se o autômato é determinístico.

        Um AFD não possui transições épsilon (``simbodo is None``) e não possui
        duas transições com a mesma origem e o mesmo símbodo.
        """
        if self.estado_inicial is None:
            return False
        vistos: set[tuple[Estado, str | None]] = set()
        for transicao in self.transicoes:
            if transicao.simbodo is None:
                return False
            chave = (transicao.origem, transicao.simbodo)
            if chave in vistos:
                return False
            vistos.add(chave)
        return True

    def eh_completo(self) -> bool:
        """Verifica se o autômato é completo (toda origem tem transição para
        todo símbodo do alfabeto)."""
        existentes: set[tuple[Estado, str | None]] = set()
        for transicao in self.transicoes:
            if transicao.simbodo is not None:
                existentes.add((transicao.origem, transicao.simbodo))
        for estado in self.estados:
            for simbodo in self.alfabeto:
                if (estado, simbodo) not in existentes:
                    return False
        return True
