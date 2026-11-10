import { useEffect, useRef, useState } from "react";
import api from "../../api/axiosConfig";
import { usarSessao } from "../../components/Sessao";
import Mensagens, { mensagemErro } from "../../components/Mensagens";

const STATUS_DOCUMENTO = {
  pendente: { texto: "Pendente", classe: "pending" },
  aprovado: { texto: "Aprovado", classe: "active" },
  rejeitado: { texto: "Rejeitado", classe: "inactive" },
};

export default function MeiaEntrada() {
  const { usuario } = usarSessao(); const arquivo = useRef();
  const [regras, setRegras] = useState(null); const [documentos, setDocumentos] = useState([]);
  const [tipo, setTipo] = useState("estudante"); const [validade, setValidade] = useState("");
  const [observacoes, setObservacoes] = useState({});
  const [erro, setErro] = useState(""); const [sucesso, setSucesso] = useState(""); const [ocupado, setOcupado] = useState(false);
  async function carregar() { try { const [r, d] = await Promise.all([api.get("/meia/regras"), api.get("/meia/documentos")]); setRegras(r.data); setDocumentos(d.data); } catch (e) { setErro(mensagemErro(e)); } }
  useEffect(() => { carregar(); }, []);
  async function enviar(evento) {
    evento.preventDefault(); setErro(""); setSucesso(""); setOcupado(true);
    try { const dados = new FormData(); dados.append("arquivo", arquivo.current.files[0]); dados.append("tipo", tipo); dados.append("validade", validade);
      await api.post("/meia/documentos", dados, { headers: { "Content-Type": "multipart/form-data" } });
      arquivo.current.value = ""; setSucesso("Comprovante enviado. Aguarde a análise do administrador."); await carregar();
    } catch (e) { setErro(mensagemErro(e)); } finally { setOcupado(false); }
  }
  async function analisar(id, status) {
    const observacao = (observacoes[id] || "").trim();
    setErro(""); setSucesso("");
    if (status === "rejeitado" && !observacao) {
      setErro("Informe o motivo da rejeição no campo Observação da análise."); return;
    }
    setOcupado(true);
    try {
      await api.put(`/meia/documentos/${id}`, { status, observacao });
      setDocumentos(atuais => atuais.map(doc => doc.id === id ? { ...doc, status, observacao } : doc));
      setSucesso(status === "aprovado" ? "Comprovante aprovado." : "Comprovante rejeitado."); await carregar();
    }
    catch (e) { setErro(mensagemErro(e)); } finally { setOcupado(false); }
  }
  async function baixar(id, nome) {
    try { const r = await api.get(`/meia/documentos/${id}/arquivo`, { responseType: "blob" }); const url = URL.createObjectURL(r.data);
      const a = document.createElement("a"); a.href = url; a.download = nome; a.click(); URL.revokeObjectURL(url);
    } catch (e) { setErro("Não foi possível baixar o documento."); }
  }
  return <><div className="page-title"><span className="eyebrow">BENEFÍCIOS</span><h1>Central de meia-entrada</h1></div><Mensagens erro={erro} sucesso={sucesso} />
    <section className="card"><h2>Regras e comprovação</h2><p className="muted">Confirme os critérios e documentos com o organizador.</p><ul>{regras?.categorias.map(regra => <li key={regra.tipo}><strong>{regra.titulo}:</strong> {regra.descricao}</li>)}</ul>
      <p>O desconto é de 50% no ingresso. O comprovante deve estar aprovado e válido na data do evento, inclusive no pagamento.</p></section>
    <section className="card"><h2>Enviar comprovante</h2><p className="muted">PDF, JPG ou PNG de até 2 MB.</p>
      <form onSubmit={enviar} className="two-columns"><label className="form-group">Categoria<select value={tipo} onChange={e => setTipo(e.target.value)}>{regras?.categorias.map(regra => <option key={regra.tipo} value={regra.tipo}>{regra.titulo}</option>)}</select></label>
        <label className="form-group">Validade<input type="date" value={validade} onChange={e => setValidade(e.target.value)} required /></label>
        <label className="form-group">Arquivo<input type="file" accept=".pdf,.jpg,.jpeg,.png" ref={arquivo} required /></label><div><button className="btn btn-primary" disabled={ocupado}>Enviar para análise</button></div></form></section>
    <section className="card"><h2>{usuario.papel === "admin" ? "Análise de documentos" : "Meus documentos"}</h2>{!documentos.length && <p>Nenhum documento enviado.</p>}
      {documentos.map(doc => {
        const status = STATUS_DOCUMENTO[doc.status] || { texto: doc.status, classe: "" };
        const categoria = regras?.categorias.find(regra => regra.tipo === doc.tipo)?.titulo || doc.tipo;
        return <article className="reservation" key={doc.id}>
          <div className="document-info">
            <div className="document-heading"><h3>{doc.titular} · {categoria}</h3><span className={`status-badge ${status.classe}`}>{status.texto}</span></div>
            <p className="muted small">{doc.nome_arquivo} · Válido até {doc.validade.split("-").reverse().join("/")}</p>
            {(doc.status !== "pendente" || doc.observacao) && <p className="document-observation"><strong>{doc.status === "rejeitado" ? "Motivo da rejeição:" : "Observação da análise:"}</strong>{" "}{doc.observacao || "Nenhuma observação registrada."}</p>}
            <button className="btn btn-secondary" onClick={() => baixar(doc.id, doc.nome_arquivo)}>Baixar comprovante</button>
          </div>
          {usuario.papel === "admin" && doc.status === "pendente" && <div className="document-review-actions" aria-busy={ocupado}>
            <label className="form-group">Observação da análise
              <textarea rows={3} value={observacoes[doc.id] || ""} onChange={e => setObservacoes({ ...observacoes, [doc.id]: e.target.value })} maxLength={300} disabled={ocupado}
                placeholder="Informe uma observação ou o motivo da rejeição." aria-describedby={`observacao-ajuda-${doc.id}`} />
            </label>
            <p className="small muted" id={`observacao-ajuda-${doc.id}`}>Opcional ao aprovar. Obrigatória para rejeitar.</p>
            <div className="actions"><button className="btn btn-primary" disabled={ocupado} onClick={() => analisar(doc.id, "aprovado")}>Aprovar</button>
              <button className="btn btn-danger" disabled={ocupado} onClick={() => analisar(doc.id, "rejeitado")}>Rejeitar</button></div>
          </div>}
        </article>;
      })}</section></>;
}
