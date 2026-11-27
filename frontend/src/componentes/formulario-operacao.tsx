import BotaoPrincipal from "./botao-principal";
import "./formulario-operacao.css";
import PainelImportacao from "./importacao/painel-importacao";
import PainelSelecao from "./selecao/painel-selecao";
import { useState } from "react";
//import abrirPdfIcone from "../assets/abrir-pdf.svg";
import baixarAutomatoIcone from "../assets/automato-baixar.svg";

interface FormOperacaoState {
  operacao: string;
  arquivo: File | null;
  enviando: boolean;
  erro: string | null;
  urlDownload: string | null;
  urlJff: string | null;
  urlPdf: string | null;
  nomeBase: string | null;
}

function FormularioOperacao() {
  const [state, setState] = useState<FormOperacaoState>({
    operacao: "",
    arquivo: null,
    enviando: false,
    erro: null,
    urlDownload: null,
    urlJff: null,
    urlPdf: null,
    nomeBase: null,
  });

  function handleSelecionarOperacao(operacao: string) {
    setState((s) => ({
      ...s,
      operacao,
      arquivo: null,
      enviando: false,
      erro: null,
      urlDownload: null,
      urlJff: null,
      urlPdf: null,
      nomeBase: null,
    }));
  }

  function handleSelecionarArquivo(arquivo: File | null) {
    setState((s) => ({
      ...s,
      arquivo,
      erro: null,
      urlDownload: null,
      urlJff: null,
      urlPdf: null,
      nomeBase: null,
    }));
  }

  async function handleEnviar() {
    const { operacao, arquivo, enviando } = state;

    if (!arquivo) {
      setState((s) => ({
        ...s,
        erro: "Selecione um arquivo .jff antes de gerar.",
      }));
      return;
    }

    if (enviando) return;

    setState((s) => ({ ...s, enviando: true, erro: null }));

    const formData = new FormData();
    formData.append("arquivo", arquivo);

    try {
      const resposta = await fetch(`/operacoes/${operacao}`, {
        method: "POST",
        body: formData,
      });

      if (!resposta.ok) {
        const texto = await resposta.text();

        setState((s) => ({
          ...s,
          enviando: false,
          erro: texto,
        }));
        return;
      }

      const blob = await resposta.blob();
      const url = URL.createObjectURL(blob);

      setState((s) => ({
        ...s,
        enviando: false,
        urlDownload: url,
      }));
    } catch {
      setState((s) => ({
        ...s,
        enviando: false,
        erro: "Erro ao comunicar com o backend",
      }));
    }
  }

  function handleDownload() {
    const { urlJff, nomeBase } = state;

    if (!urlJff || !nomeBase) return;

    const a = document.createElement("a");
    a.href = urlJff;
    a.download = `${nomeBase}.jff`;

    document.body.append(a);
    a.click();
    a.remove();
  }

  function handleAbrirPdf() {
    const { urlPdf } = state;

    if (!urlPdf) return;

    window.open(urlPdf, "_blank");
  }

  return (
    <article className="formulario-operacao">
      <div className="paineis-container">
        {state.operacao && (
          <PainelImportacao
            key={state.operacao}
            quantidadeSlots={1}
            onArquivoSelecionado={handleSelecionarArquivo}
          />
        )}

        <PainelSelecao
          valor={state.operacao}
          onSelecionar={handleSelecionarOperacao}
        />
      </div>

      <div className="botao-gerar-automato">
        <BotaoPrincipal
          label="Gerar Autômato"
          disabled={state.enviando || !state.arquivo}
          onClick={handleEnviar}
          className="gerar-automato"
        />

        {state.urlDownload && (
          <div className="botoes-baixar-abrir">
            <BotaoPrincipal
              label="Baixar autômato"
              onClick={handleDownload}
              className="baixar-automato"
              icon={<img src={baixarAutomatoIcone} alt="" aria-hidden="true" />}
            />

            <BotaoPrincipal
              label="Abrir PDF"
              onClick={handleAbrirPdf}
              className="abrir-pdf"
              //icon={<img src={abrirPdfIcone} alt="" aria-hidden="true" />}
            />
          </div>
        )}

        {state.erro && <p role="status">{state.erro}</p>}
      </div>
    </article>
  );
}

export default FormularioOperacao;