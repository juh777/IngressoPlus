import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import api from "../../api/axiosConfig";
import { usarSessao } from "../../components/Sessao";
import Mensagens, { mensagemErro, moeda, dataHora } from "../../components/Mensagens";
import MapaAssentos from "../../components/MapaAssentos";
import GestaoEvento from "../../components/GestaoEvento";

export default function EventoDetalhe() {
  const { id } = useParams(); const navigate = useNavigate(); const { usuario } = usarSessao();
  const [evento, setEvento] = useState(null); const [lotes, setLotes] = useState([]); const [assentos, setAssentos] = useState([]);
  const [loteId, setLoteId] = useState(""); const [assentoId, setAssentoId] = useState(null);
  const [quantidade, setQuantidade] = useState(1); const [tipo, setTipo] = useState("inteira");
  const [taxas, setTaxas] = useState([]); const [confirmar, setConfirmar] = useState(false);
  const [erro, setErro] = useState(""); const [sucesso, setSucesso] = useState(""); const [ocupado, setOcupado] = useState(false);
  const [carregando, setCarregando] = useState(true);
  async function carregar() {
    try {
      const [eventoResp, lotesResp, mapaResp] = await Promise.all([
        api.get(`/eventos/${id}`), api.get(`/eventos/${id}/lotes`), api.get(`/eventos/${id}/assentos`),
      ]);
      setEvento(eventoResp.data); setLotes(lotesResp.data); setAssentos(mapaResp.data);
      setAssentoId(atual => mapaResp.data.some(item => item.id === atual && item.status === "disponivel") ? atual : null);
    } catch (e) { setErro(mensagemErro(e)); } finally { setCarregando(false); }
  }
  useEffect(() => { carregar(); const intervalo = setInterval(carregar, 10000); return () => clearInterval(intervalo); }, [id]);
  useEffect(() => {
    if (!loteId) { setTaxas([]); return; }
    let ativo = true;
    api.get(`/lotes/${loteId}/taxas`, { params: { quantidade, tipo } }).then(r => { if (ativo) setTaxas(r.data); })
      .catch(e => { if (ativo) setErro(mensagemErro(e)); });
    return () => { ativo = false; };
  }, [loteId, quantidade, tipo]);
  async function reservar(expressa) {
    if (!usuario) { navigate("/login", { state: { voltar: `/eventos/${id}` } }); return; }
    setOcupado(true); setErro(""); setSucesso("");
    try {
      const dados = { lote_id: Number(loteId), quantidade: Number(quantidade), tipo, assento_id: assentoId };
      if (expressa) { dados.confirmar_simulacao = confirmar; await api.post("/checkout/expressa", dados); }
      else await api.post("/reservas", dados);
      navigate("/meus-ingressos", { state: { mensagem: expressa ? "Compra simulada aprovada. Seus ingressos estão disponíveis." : "Reserva criada por 15 minutos. Simule o pagamento para emitir os ingressos." } });
    } catch (e) { setErro(mensagemErro(e)); await carregar(); } finally { setOcupado(false); }
  }
  async function avisar(lote = null) {
    if (!usuario) { navigate("/login", { state: { voltar: `/eventos/${id}` } }); return; }
    setOcupado(true); setErro(""); setSucesso("");
    try { await api.post("/alertas", { evento_id: Number(id), lote_id: lote }); setSucesso("Alerta agendado. Acompanhe na área de alertas."); }
    catch (e) { setErro(mensagemErro(e)); } finally { setOcupado(false); }
  }
  if (carregando) return <p role="status">Carregando evento…</p>;
  if (!evento) return <><Mensagens erro={erro} /><Link to="/eventos">Voltar aos eventos</Link></>;
  const lote = lotes.find(item => item.id === Number(loteId));
  const total = taxas.find(item => item.canal === "Ingresso+");
  const podeReservar = lote?.aberto && lote.disponiveis >= Number(quantidade) && (!assentos.length || assentoId);
  return <><Link to="/eventos" className="back-link">← Todos os eventos</Link>
    <header className="card event-hero"><span className="eyebrow">{evento.categoria || "EXPERIÊNCIA INGRESSO+"}</span><h1>{evento.nome}</h1>
      <p>{dataHora(evento.data_hora_evento)} · {evento.local}</p><p>{evento.descricao || "Escolha seu ingresso e reserve seu lugar."}</p>
      {!evento.ativo && <div className="error-msg">Evento inativo. Novas compras estão indisponíveis.</div>}
      <button className="btn btn-secondary" onClick={() => avisar()} disabled={ocupado || !evento.ativo}>Avise-me sobre a abertura</button></header>
    <Mensagens erro={erro} sucesso={sucesso} />
    {usuario?.papel === "admin" && <GestaoEvento evento={evento} aoAtualizar={carregar} />}
    <section className="card"><h2>Lotes e disponibilidade</h2><p className="muted">Estoque atualizado automaticamente a cada 10 segundos.</p>
      {!lotes.length && <p>O organizador ainda não cadastrou lotes para este evento.</p>}
      <div className="lot-grid">{lotes.map(item => <article key={item.id} className={`lot-card ${Number(loteId) === item.id ? "chosen" : ""}`}>
        <h3>{item.nome}</h3><strong className="price">{moeda(item.preco)}</strong><p>{item.disponiveis} de {item.quantidade} disponíveis</p>
        <p className="small muted">{dataHora(item.inicio)} até {dataHora(item.fim)}</p><span className={`status-badge ${item.aberto ? "active" : "inactive"}`}>{item.aberto ? "Vendas abertas" : "Fora do período de venda"}</span>
        <div className="actions"><button className="btn btn-primary" disabled={!item.aberto || item.disponiveis < 1} onClick={() => setLoteId(String(item.id))}>{Number(loteId) === item.id ? "Lote selecionado" : "Selecionar lote"}</button>
          <button className="btn btn-secondary" onClick={() => avisar(item.id)} disabled={ocupado}>Alerta deste lote</button></div></article>)}</div></section>
    <section className="card"><h2>Escolha seu lugar</h2><MapaAssentos assentos={assentos} selecionado={assentoId} aoSelecionar={setAssentoId} desabilitado={ocupado} /></section>
    <section className="card"><h2>Seu ingresso</h2><div className="two-columns">
      <label className="form-group">Modalidade<select value={tipo} onChange={e => setTipo(e.target.value)}><option value="inteira">Inteira</option><option value="meia">Meia-entrada (documento aprovado)</option></select></label>
      <label className="form-group">Quantidade<input type="number" min={1} max={assentos.length ? 1 : 10} value={quantidade} onChange={e => setQuantidade(e.target.value)} disabled={Boolean(assentos.length)} /></label></div>
      <p className="small"><Link to="/meia-entrada">Consulte as regras e envie seu comprovante de meia-entrada.</Link></p>
      {taxas.length > 0 && <><h3>Comparador de taxas</h3><p className="muted small">Valores ilustrativos. Os canais A e B são simulações, sem consulta a preços externos.</p>
        <div className="table-responsive"><table><thead><tr><th>Canal</th><th>Ingressos</th><th>Taxa total</th><th>Total</th></tr></thead><tbody>
          {taxas.map(item => <tr key={item.canal}><td>{item.canal}</td><td>{moeda(item.subtotal)}</td><td>{moeda(item.taxa)}</td><td><strong>{moeda(item.total)}</strong></td></tr>)}
        </tbody></table></div></>}
      <div className="checkout-summary"><strong>Total estimado: {moeda(total?.total)}</strong><p className="muted small">O valor é confirmado pelo servidor ao reservar. A reserva dura 15 minutos.</p>
        <button className="btn btn-primary" disabled={ocupado || !podeReservar} onClick={() => reservar(false)}>Reservar ingresso</button>
        <label className="check-label"><input type="checkbox" checked={confirmar} onChange={e => setConfirmar(e.target.checked)} /> Confirmo a simulação de compra expressa, sem cobrança real.</label>
        <button className="btn btn-secondary" disabled={ocupado || !podeReservar || !confirmar} onClick={() => reservar(true)}>Compra expressa em 1 clique</button></div>
    </section></>;
}
