from typing import Annotated

from fastapi import APIRouter, File, Form, Response, UploadFile

from api.servicos.operacoes_servico import complemento
from api.nucleo.excecoes import OperacaoInvalidaError

router = APIRouter(prefix="/operacoes", tags=["Operações"])


@router.post("/complemento")
async def realizar_complemento(
    arquivo: Annotated[UploadFile, File()],
    alfabeto: Annotated[str | None, Form()] = None,
) -> Response:
    """Gera um .zip com o .jff do complemento e o relatório PDF das etapas."""
    jff = (await arquivo.read()).decode("utf-8")

    alfabeto_final = None
    if alfabeto:
        alfabeto_final = {s.strip() for s in alfabeto.split(",") if s.strip()}
        if not alfabeto_final:
            raise OperacaoInvalidaError("Alfabeto não pode ser vazio.")

    resposta = complemento(jff, alfabeto=alfabeto_final)

    return Response(
        content=resposta.compactar("complemento"),
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="complemento.zip"'},
    )
