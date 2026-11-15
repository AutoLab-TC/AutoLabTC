from dataclasses import dataclass

from api.nucleo.estado import Estado


@dataclass(frozen=True)
class Transicao:
    """Representa uma transição de um autômato finito.

    simbolo=None representa uma transição épsilon (AFN).
    """

    origem: Estado
    simbolo: str | None
    destino: Estado
