import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../../api/axiosConfig";
import Mensagens, { mensagemErro, moeda } from "../../components/Mensagens";

export default function Grupos() {
  const [grupos, setGrupos] = useState([]); const [eventos, setEventos] = useState([]); const [detalhe, setDetalhe] = useState(null);
  const [nome, setNome] = useState(""); const [eventoId, setEventoId] = useState(""); const [codigo, setCodigo] = useState("");
  const [erro, setErro] = useState(""); const [sucesso, setSucesso] = useState(""); const [ocupado, setOcupado] = useState(false);
  async function carregar() { try { const [g, e] = await Promise.all([api.get("/grupos"), api.get("/eventos")]); setGrupos(g.data); setEventos(e.data.filter(item => item.ativo)); } catch (e) { setErro(mensagemErro(e)); } }
  useEffect(() => { carregar(); }, []);
  async function ver(id) { try { const r = await api.get(`/grupos/${id}`); setDetalhe(r.data); } catch (e) { setErro(mensagemErro(e)); } }
  async function enviar(evento, entrar) {
    evento.preventDefault(); setOcupado(true); setErro(""); setSucesso("");
    try { const r = await api.post(entrar ? "/grupos/entrar" : "/grupos", entrar ? { codigo } : { nome, evento_id: Number(eventoId) });
      setSucesso(entrar ? "Participação confirmada." : "Grupo criado. Compartilhe o código com seus convidados."); await carregar(); await ver(r.data.id);
    } catch (e) { setErro(mensagemErro(e)); } finally { setOcupado(false); }
  }
  async function sair(id) { setOcupado(true); setErro(""); try { await api.post(`/grupos/${id}/sair`); setDetalhe(null); await carregar(); setSucesso("Você saiu do grupo."); } catch (e) { setErro(mensagemErro(e)); } finally { setOcupado(false); } }
  return <><div className="page-title"><span className="eyebrow">JUNTOS NO EVENTO</span><h1>Grupos de compra</h1><p className="muted">Organizem a ida ao mesmo evento. Cada pessoa faz e acompanha o próprio pagamento.</p></div>
    <Mensagens erro={erro} sucesso={sucesso} /><div className="two-columns"><section className="card"><h2>Criar grupo</h2><form onSubmit={e => enviar(e, false)}>
      <label className="form-group">Nome do grupo<input value={nome} onChange={e => setNome(e.target.value)} maxLength={100} required /></label>
      <label className="form-group">Evento<select value={eventoId} onChange={e => setEventoId(e.target.value)} required><option value="">Selecione</option>{eventos.map(evento => <option key={evento.id} value={evento.id}>{evento.nome}</option>)}</select></label>
      <button className="btn btn-primary" disabled={ocupado}>Criar grupo</button></form></section>
      <section className="card"><h2>Entrar com código</h2><form onSubmit={e => enviar(e, true)}><label className="form-group">Código de convite<input value={codigo} onChange={e => setCodigo(e.target.value.toUpperCase())} maxLength={24} required /></label><button className="btn btn-secondary" disabled={ocupado}>Participar</button></form><p className="muted">Até 20 participantes. Somente membros conseguem ver o painel do grupo.</p></section></div>
    <section className="card"><h2>Meus grupos</h2>{!grupos.length && <p>Crie um grupo ou entre com um código.</p>}<div className="lot-grid">{grupos.map(grupo => <article className="lot-card" key={grupo.id}><h3>{grupo.nome}</h3><p>{grupo.evento}</p><button className="btn btn-primary" onClick={() => ver(grupo.id)}>Abrir painel</button></article>)}</div></section>
    {detalhe && <section className="card"><h2>{detalhe.nome}</h2><p>Convite: <strong className="invite-code">{detalhe.codigo}</strong></p><Link to={`/eventos/${detalhe.evento_id}`}>Escolher ingresso para {detalhe.evento}</Link>
      <div className="table-responsive"><table><thead><tr><th>Participante</th><th>Ingressos pagos</th><th>Total individual</th></tr></thead><tbody>{detalhe.membros.map(membro => <tr key={membro.id}><td>{membro.nome}</td><td>{membro.ingressos}</td><td>{moeda(membro.total_pago)}</td></tr>)}</tbody></table></div>
      <p className="muted small">O painel considera as compras de cada participante neste evento; não há transferência de dinheiro entre membros.</p><button className="btn btn-secondary" disabled={ocupado} onClick={() => sair(detalhe.id)}>Sair do grupo</button></section>}</>;
}
