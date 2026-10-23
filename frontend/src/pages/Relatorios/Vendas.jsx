import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../../api/axiosConfig";
import Mensagens, { mensagemErro, moeda } from "../../components/Mensagens";

export default function Vendas() {
  const [eventos, setEventos] = useState([]); const [eventoId, setEventoId] = useState(""); const [relatorio, setRelatorio] = useState(null);
  const [erro, setErro] = useState(""); const [carregando, setCarregando] = useState(false);
  useEffect(() => { api.get("/eventos").then(r => setEventos(r.data)).catch(e => setErro(mensagemErro(e))); }, []);
  async function consultar(evento) { evento.preventDefault(); setCarregando(true); setErro(""); setRelatorio(null);
    try { const r = await api.get(`/relatorios/vendas/${eventoId}`); setRelatorio(r.data); }
    catch (e) { setErro(mensagemErro(e)); } finally { setCarregando(false); }
  }
  return <><div className="page-title"><span className="eyebrow">GESTÃO</span><h1>Relatório de vendas</h1><Link to="/relatorios">Ver também o relatório de categorias e status</Link></div><Mensagens erro={erro} />
    <section className="card"><form onSubmit={consultar} className="filter-form"><label className="form-group">Evento<select value={eventoId} onChange={e => setEventoId(e.target.value)} required><option value="">Selecione</option>{eventos.map(evento => <option key={evento.id} value={evento.id}>{evento.nome}</option>)}</select></label><button className="btn btn-primary" disabled={carregando}>{carregando ? "Consultando…" : "Consultar vendas"}</button></form></section>
    {relatorio && <><div className="report-summary">{[["Ingressos vendidos", relatorio.ingressos], ["Arrecadação simulada", moeda(relatorio.arrecadacao)], ["Taxas incluídas", moeda(relatorio.taxas)]].map(([titulo, valor]) =>
      <article className="card report-metric" key={titulo}><p className="report-metric-label">{titulo}</p><p className="report-metric-value">{valor}</p></article>)}</div>
      <section className="card"><h2>Resultado por lote</h2><p>{relatorio.compras} compra(s) aprovada(s). Cancelamentos e recusas não entram na arrecadação.</p>
        <div className="table-responsive"><table><thead><tr><th>Lote</th><th>Capacidade</th><th>Vendidos</th><th>Receita simulada</th></tr></thead><tbody>{relatorio.por_lote.map(lote => <tr key={lote.id}><td>{lote.nome}</td><td>{lote.quantidade}</td><td>{lote.vendidos}</td><td>{moeda(lote.receita)}</td></tr>)}</tbody></table></div></section>
      <section className="card"><h2>Reservas por situação</h2>{relatorio.reservas_por_status.length ? <ul>{relatorio.reservas_por_status.map(item => <li key={item.status}>{item.status}: {item.total}</li>)}</ul> : <p>Este evento ainda não possui reservas.</p>}</section></>}
  </>;
}
