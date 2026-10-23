import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/axiosConfig";
import { usarSessao } from "./Sessao";

export default function Recomendacoes() {
  const { usuario } = usarSessao(); const [resultado, setResultado] = useState(null);
  useEffect(() => { if (!usuario) { setResultado(null); return; }
    api.get("/recomendacoes").then(r => setResultado(r.data)).catch(() => setResultado(null));
  }, [usuario]);
  if (!resultado?.eventos.length) return null;
  return <section className="card recommendations"><span className="eyebrow">PARA VOCÊ</span><h2>Descubra seu próximo evento</h2>
    <p className="muted small">{resultado.origem}. Ajuste seus interesses no perfil.</p><div className="lot-grid">{resultado.eventos.map(evento =>
      <Link className="recommendation-card" key={evento.id} to={`/eventos/${evento.id}`}><span className="eyebrow">{evento.categoria || "EVENTO"}</span><h3>{evento.nome}</h3><p>{evento.motivo}</p><strong>Explorar evento →</strong></Link>)}</div></section>;
}
