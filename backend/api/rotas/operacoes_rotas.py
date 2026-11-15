from typing import Annotated

from fastapi import APIRouter, File, Form, Response, UploadFile

from api.servicos.operacoes_servico import complemento

router = APIRouter(prefix="/operacoes", tags=["Operações"])

@router.post("/complemento")
async def realizar_complemento(
    arquivo: Annotated[UploadFile, File()],
    alfabeto: Annotated[str | None, Form()] = None,
) -> Response:
    """Gera um .zip com o .jff do complemento e o relatório PDF das etapas."""
    arquivo_bytes = await arquivo.read()
    resposta = complemento(arquivo_bytes, alfabeto=alfabeto)

    return Response(
        content=resposta.compactar("complemento"),
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="complemento.zip"'},
    )
