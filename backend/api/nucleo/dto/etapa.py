from dataclasses import dataclass

from api.nucleo.automato_finito import AutomatoFinito


# Representa uma etapa intermediária de uma operação sobre autômato.

# Atributos:
#     titulo: Título curto da etapa.
#     descricao: Descrição textual/explicativa da etapa.
#     automato: Cópia do autômato no estado correspondente à etapa.

@dataclass
class Etapa:
    titulo: str
    descricao: str
    automato: AutomatoFinito
