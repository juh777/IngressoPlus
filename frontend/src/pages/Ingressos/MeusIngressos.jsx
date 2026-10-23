import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import api from "../../api/axiosConfig";
import { usarSessao } from "../../components/Sessao";
import Mensagens, { mensagemErro, moeda, dataHora } from "../../components/Mensagens";

export default function MeusIngressos() {
  const local = useLocation(); const { usuario } = usarSessao();
  const [reservas, setReservas] = useState([]); const [ingressos, setIngressos] = useState([]);
  const [erro, setErro] = useState(""); const [sucesso, setSucesso] = useState(local.state?.mensagem || "");
  const [ocupado, setOcupado] = useState(false); const [codigo, setCodigo] = useState("");
  const [carregando, setCarregando] = useState(true);
  async function carregar() {
    try { const [r, i] = await Promise.all([api.get("/reservas"), api.get("/ingressos")]); setReservas(r.data); setIngressos(i.data); }
    catch (e) { setErro(mensagemErro(e)); } finally { setCarregando(false); }
  }
  useEffect(() => { carregar(); const timer = setInterval(carregar, 15000); return () => clearInterval(timer); }, []);
  async function agir(reservaId, acao, resultado) {
    setOcupado(true); setErro(""); setSucesso("");
    try { const r = await api.post(`/reservas/${reservaId}/${acao}`, { resultado });
      setSucesso(acao === "cancelar" ? r.data.mensagem : r.data.status === "aprovado" ? "Pagamento simulado aprovado. Ingressos emitidos." : "Simulação recusada. Você pode tentar novamente antes de expirar."); await carregar();
    } catch (e) { setErro(mensagemErro(e)); } finally { setOcupado(false); }
  }
  async function validar(evento) {
    evento.preventDefault(); setOcupado(true); setErro("");
    try { const r = await api.post("/ingressos/validar", { codigo: codigo.trim() }); setSucesso(`${r.data.mensagem} ${r.data.titular} — ${r.data.evento}`); await carregar(); }
    catch (e) { setErro(mensagemErro(e)); } finally { setOcupado(false); }
  }
  return <><div className="page-title"><span className="eyebrow">SUA CARTEIRA</span><h1>Meus ingressos e reservas</h1></div>
    <div className="demo-note">Demonstração: pagamentos e estornos são simulados. Nenhum cartão é solicitado ou armazenado.</div>
    <Mensagens erro={erro} sucesso={sucesso} />{carregando && <p role="status">Carregando compras…</p>}
    <section className="card"><h2>Reservas e pagamentos</h2>{!reservas.length && !carregando && <p>Você ainda não possui reservas. <Link to="/eventos">Explore os eventos.</Link></p>}
      {reservas.map(reserva => <article className="reservation" key={reserva.id}><div><h3>{reserva.evento}</h3>
        <p>Reserva #{reserva.id} · {reserva.quantidade} ingresso(s) · {reserva.tipo} · {reserva.lote}</p>
        <p><span className={`status-badge ${reserva.status === "paga" ? "active" : "inactive"}`}>{reserva.status}</span> <strong>{moeda(reserva.total)}</strong></p>
        {reserva.status === "reservada" && <p className="small">Pague até {dataHora(reserva.expira_em)}. Depois, o estoque é liberado.</p>}
      </div><div className="actions">{reserva.status === "reservada" && <><button className="btn btn-primary" disabled={ocupado} onClick={() => agir(reserva.id, "pagamento", "aprovado")}>Simular aprovação</button>
        <button className="btn btn-secondary" disabled={ocupado} onClick={() => agir(reserva.id, "pagamento", "recusado")}>Simular recusa</button></>}
        {["reservada", "paga"].includes(reserva.status) && <button className="btn btn-danger" disabled={ocupado} onClick={() => agir(reserva.id, "cancelar")}>Cancelar {reserva.status === "paga" ? "compra simulada" : "reserva"}</button>}</div></article>)}</section>
    <section className="card"><h2>Ingressos emitidos</h2>{!ingressos.length && <p>Seus ingressos aparecem aqui após a aprovação do pagamento.</p>}
      <div className="ticket-grid">{ingressos.map(ingresso => <article className="ticket" key={ingresso.id}><span className="eyebrow">INGRESSO+ · #{ingresso.id}</span><h3>{ingresso.evento}</h3>
        <p>{dataHora(ingresso.data_hora_evento)}<br />{ingresso.local}</p><p>{ingresso.fila ? `${ingresso.setor} · ${ingresso.fila}${ingresso.numero}` : "Entrada geral"} · {ingresso.tipo}</p>
        <p className="ticket-code">{ingresso.codigo}</p><p className="small">{ingresso.status === "cancelada" ? "Cancelado — código inválido" : ingresso.utilizado_em ? `Utilizado em ${dataHora(ingresso.utilizado_em)}` : "Apresente este código na entrada."}</p></article>)}</div>
      {ingressos.length > 0 && <button className="btn btn-secondary no-print" onClick={() => window.print()}>Imprimir carteira</button>}</section>
    {usuario.papel === "admin" && <section className="card"><h2>Portaria: validar ingresso</h2><p>A confirmação registra a utilização. O mesmo código só pode ser usado uma vez.</p>
      <form className="filter-form" onSubmit={validar}><label className="form-group">Código do ingresso<input value={codigo} onChange={e => setCodigo(e.target.value)} required /></label>
        <button className="btn btn-primary" disabled={ocupado}>Confirmar entrada</button></form></section>}</>;
}
