import { useState } from "react";
import api from "../api/axiosConfig";
import Mensagens, { mensagemErro } from "./Mensagens";

export default function GestaoEvento({ evento, aoAtualizar }) {
  const [lote, setLote] = useState({ nome: "", preco: "", quantidade: 30, taxa_percentual: 10, inicio: "", fim: "" });
  const [mapa, setMapa] = useState({ setor: "Plateia", filas: 3, por_fila: 10 });
  const [erro, setErro] = useState(""); const [sucesso, setSucesso] = useState(""); const [ocupado, setOcupado] = useState(false);
  async function enviar(event, recurso, dados) {
    event.preventDefault(); setOcupado(true); setErro(""); setSucesso("");
    try {
      const corpo = { ...dados };
      if (recurso === "lotes") { corpo.inicio = new Date(dados.inicio).toISOString(); corpo.fim = new Date(dados.fim).toISOString(); }
      await api.post(`/eventos/${evento.id}/${recurso}`, corpo); setSucesso("Configuração salva."); await aoAtualizar();
    } catch (e) { setErro(mensagemErro(e)); } finally { setOcupado(false); }
  }
  return <details className="card admin-panel"><summary>Administração: configurar lotes e mapa</summary><Mensagens erro={erro} sucesso={sucesso} />
    <div className="two-columns"><form onSubmit={e => enviar(e, "lotes", lote)}><h3>Novo lote</h3>
      {[["nome", "Nome", "text"], ["preco", "Preço (R$)", "number"], ["quantidade", "Quantidade", "number"], ["taxa_percentual", "Taxa (%)", "number"], ["inicio", "Início das vendas", "datetime-local"], ["fim", "Fim das vendas", "datetime-local"]].map(([campo, titulo, tipo]) =>
        <label className="form-group" key={campo}>{titulo}<input type={tipo} value={lote[campo]} required step={tipo === "number" ? "0.01" : undefined}
          onChange={e => setLote({ ...lote, [campo]: e.target.value })} /></label>)}
      <button className="btn btn-primary" disabled={ocupado}>Cadastrar lote</button></form>
      <form onSubmit={e => enviar(e, "assentos", mapa)}><h3>Mapa numerado</h3><p className="muted">Crie uma única vez, antes da primeira reserva. Até 10 filas e 20 lugares por fila.</p>
        {[["setor", "Setor", "text"], ["filas", "Filas", "number"], ["por_fila", "Lugares por fila", "number"]].map(([campo, titulo, tipo]) =>
          <label className="form-group" key={campo}>{titulo}<input type={tipo} value={mapa[campo]} required onChange={e => setMapa({ ...mapa, [campo]: e.target.value })} /></label>)}
        <button className="btn btn-secondary" disabled={ocupado}>Criar mapa de assentos</button></form></div></details>;
}
