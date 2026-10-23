export default function MapaAssentos({ assentos, selecionado, aoSelecionar, desabilitado = false }) {
  if (!assentos.length) return <p className="muted">Evento com entrada geral, sem assento numerado.</p>;
  const filas = [...new Set(assentos.map(assento => assento.fila))];
  return <section className="seat-map"><div className="stage">PALCO</div>
    <div className="seat-legend"><span>○ Disponível</span><span>● Selecionado</span><span>× Ocupado</span></div>
    {filas.map(fila => <div className="seat-row" key={fila}><strong>{fila}</strong>
      {assentos.filter(assento => assento.fila === fila).map(assento => <button key={assento.id} type="button"
        title={`${assento.setor} — ${fila}${assento.numero} — ${assento.status}`}
        aria-label={`Assento ${fila}${assento.numero}, ${assento.status}`} aria-pressed={selecionado === assento.id}
        disabled={desabilitado || assento.status === "ocupado"}
        className={`seat ${selecionado === assento.id ? "selected" : ""}`}
        onClick={() => aoSelecionar(selecionado === assento.id ? null : assento.id)}>{assento.numero}</button>)}
    </div>)}<p className="muted small">O mapa é atualizado a cada 10 segundos. A disponibilidade é confirmada novamente ao reservar.</p></section>;
}
