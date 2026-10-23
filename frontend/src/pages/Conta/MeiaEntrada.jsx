import { useEffect, useRef, useState } from "react";
import api from "../../api/axiosConfig";
import { usarSessao } from "../../components/Sessao";
import Mensagens, { mensagemErro } from "../../components/Mensagens";

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
    setOcupado(true); setErro("");
    try { await api.put(`/meia/documentos/${id}`, { status, observacao: observacoes[id] || "" }); setSucesso("Análise registrada."); await carregar(); }
    catch (e) { setErro(mensagemErro(e)); } finally { setOcupado(false); }
  }
  async function baixar(id, nome) {
    try { const r = await api.get(`/meia/documentos/${id}/arquivo`, { responseType: "blob" }); const url = URL.createObjectURL(r.data);
      const a = document.createElement("a"); a.href = url; a.download = nome; a.click(); URL.revokeObjectURL(url);
    } catch (e) { setErro("Não foi possível baixar o documento."); }
  }
  return <><div className="page-title"><span className="eyebrow">BENEFÍCIOS</span><h1>Central de meia-entrada</h1></div><Mensagens erro={erro} sucesso={sucesso} />
    <section className="card"><h2>Regras e comprovação</h2><p className="muted">{regras?.aviso}</p><ul>{regras?.categorias.map(regra => <li key={regra.tipo}><strong>{regra.titulo}:</strong> {regra.descricao}</li>)}</ul>
      <p>Na demonstração, o desconto é de 50% no ingresso. O comprovante deve estar aprovado e válido na data do evento, inclusive no pagamento.</p></section>
    <section className="card"><h2>Enviar comprovante</h2><p className="muted">Use dados e documentos fictícios para testar. PDF, JPG ou PNG de até 2 MB.</p>
      <form onSubmit={enviar} className="two-columns"><label className="form-group">Categoria<select value={tipo} onChange={e => setTipo(e.target.value)}>{regras?.categorias.map(regra => <option key={regra.tipo} value={regra.tipo}>{regra.titulo}</option>)}</select></label>
        <label className="form-group">Validade<input type="date" value={validade} onChange={e => setValidade(e.target.value)} required /></label>
        <label className="form-group">Arquivo<input type="file" accept=".pdf,.jpg,.jpeg,.png" ref={arquivo} required /></label><div><button className="btn btn-primary" disabled={ocupado}>Enviar para análise</button></div></form></section>
    <section className="card"><h2>{usuario.papel === "admin" ? "Análise de documentos" : "Meus documentos"}</h2>{!documentos.length && <p>Nenhum documento enviado.</p>}
      {documentos.map(doc => <article className="reservation" key={doc.id}><div><h3>{doc.titular} · {doc.tipo}</h3><p>{doc.nome_arquivo} · Válido até {doc.validade}</p><strong>{doc.status}</strong><p>{doc.observacao}</p>
        <button className="btn btn-secondary" onClick={() => baixar(doc.id, doc.nome_arquivo)}>Baixar comprovante</button></div>
        {usuario.papel === "admin" && <div><label className="form-group">Observação<input value={observacoes[doc.id] || ""} onChange={e => setObservacoes({ ...observacoes, [doc.id]: e.target.value })} maxLength={300} /></label><div className="actions">
          <button className="btn btn-primary" disabled={ocupado} onClick={() => analisar(doc.id, "aprovado")}>Aprovar</button><button className="btn btn-danger" disabled={ocupado} onClick={() => analisar(doc.id, "rejeitado")}>Rejeitar</button></div></div>}</article>)}</section></>;
}
