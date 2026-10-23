import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../../api/axiosConfig";
import Mensagens, { mensagemErro, dataHora } from "../../components/Mensagens";

export default function Alertas() {
  const [alertas, setAlertas] = useState([]); const [eventos, setEventos] = useState([]);
  const [eventoId, setEventoId] = useState(""); const [agendado, setAgendado] = useState("");
  const [erro, setErro] = useState(""); const [sucesso, setSucesso] = useState(""); const [ocupado, setOcupado] = useState(false);
  async function carregar() { try { const r = await api.get("/alertas"); setAlertas(r.data); } catch (e) { setErro(mensagemErro(e)); } }
  useEffect(() => { carregar(); api.get("/eventos").then(r => setEventos(r.data.filter(item => item.ativo))).catch(e => setErro(mensagemErro(e)));
    const timer = setInterval(carregar, 10000); return () => clearInterval(timer); }, []);
  async function agendar(evento) { evento.preventDefault(); setOcupado(true); setErro("");
    try { const dados = { evento_id: Number(eventoId) }; if (agendado) dados.agendado_em = new Date(agendado).toISOString();
      await api.post("/alertas", dados); setSucesso("Alerta agendado dentro do sistema."); await carregar();
    } catch (e) { setErro(mensagemErro(e)); } finally { setOcupado(false); }
  }
  async function agir(id, acao) { setOcupado(true); setErro(""); try { await api.put(`/alertas/${id}`, { acao }); await carregar(); }
    catch (e) { setErro(mensagemErro(e)); } finally { setOcupado(false); } }
  return <><div className="page-title"><span className="eyebrow">NÃO PERCA A ABERTURA</span><h1>Meus alertas</h1></div><Mensagens erro={erro} sucesso={sucesso} />
    <section className="card"><h2>Novo lembrete</h2><p>Os avisos aparecem nesta página. O processador de agendamentos roda a cada 10 segundos, sem envio de e-mail.</p>
      <form className="two-columns" onSubmit={agendar}><label className="form-group">Evento<select value={eventoId} onChange={e => setEventoId(e.target.value)} required><option value="">Selecione</option>{eventos.map(evento => <option key={evento.id} value={evento.id}>{evento.nome}</option>)}</select></label>
        <label className="form-group">Quando avisar (opcional)<input type="datetime-local" value={agendado} onChange={e => setAgendado(e.target.value)} /></label><div><button className="btn btn-primary" disabled={ocupado}>Agendar alerta</button></div></form><p className="muted small">Sem data personalizada, usamos a abertura de vendas. Para um lote específico, use o botão de alerta na página do evento.</p></section>
    {!alertas.length && <section className="card"><p>Nenhum alerta criado.</p></section>}
    {alertas.map(alerta => <article className={`card notification ${alerta.status === "enviado" && !alerta.lido ? "unread" : ""}`} key={alerta.id}>
      <span className="eyebrow">{alerta.status === "enviado" ? "ABERTURA DISPONÍVEL" : alerta.status.toUpperCase()}</span><h2>{alerta.evento}</h2><p>{alerta.lote || "Abertura geral de vendas"} · {dataHora(alerta.agendado_em)}</p>
      <div className="actions"><Link className="btn btn-primary" to={`/eventos/${alerta.evento_id}`}>Ver evento</Link>
        {alerta.status === "enviado" && !alerta.lido && <button className="btn btn-secondary" onClick={() => agir(alerta.id, "ler")} disabled={ocupado}>Marcar como lido</button>}
        {alerta.status === "agendado" && <button className="btn btn-secondary" onClick={() => agir(alerta.id, "cancelar")} disabled={ocupado}>Cancelar agendamento</button>}</div></article>)}</>;
}
