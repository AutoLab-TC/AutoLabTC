from typing import Annotated

from fastapi import APIRouter, File, Form, Response, UploadFile

from api.servicos.operacoes_servico import complemento, concatenacao

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


@router.post("/concatenacao")
async def realizar_concatenacao(
    arquivo1: Annotated[UploadFile, File()],
    arquivo2: Annotated[UploadFile, File()],
    alfabeto1: Annotated[str | None, Form()] = None,
    alfabeto2: Annotated[str | None, Form()] = None,
) -> Response:
    """Gera um .zip com o .jff da concatenação e o relatório PDF das etapas."""
    arquivo1_bytes = await arquivo1.read()
    arquivo2_bytes = await arquivo2.read()
    resposta = concatenacao(
        arquivo1_bytes,
        arquivo2_bytes,
        alfabeto1=alfabeto1,
        alfabeto2=alfabeto2,
    )

    return Response(
        content=resposta.compactar("concatenacao"),
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="concatenacao.zip"'},
    )
