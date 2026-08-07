import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { listarEventos, removerEvento } from "../../api/eventoService";

function formatarData(iso) {
  if (!iso) return "-";
  return new Date(iso).toLocaleString("pt-BR");
}

function EventosList() {
  const [eventos, setEventos] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");

  const carregar = async () => {
    setCarregando(true);
    try {
      const dados = await listarEventos();
      setEventos(dados);
      setErro("");
    } catch (e) {
      setErro("Nao foi possivel carregar os eventos.");
    } finally {
      setCarregando(false);
    }
  };

  useEffect(() => {
    carregar();
  }, []);

  const excluir = async (id) => {
    if (!window.confirm("Deseja realmente excluir este evento?")) return;
    try {
      await removerEvento(id);
      carregar();
    } catch (e) {
      setErro(e.response?.data?.erro || "Nao foi possivel excluir o evento.");
    }
  };

  return (
    <div>
      <div className="card" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h2 style={{ margin: 0 }}>Eventos</h2>
        <Link className="btn btn-primary" to="/eventos/novo">
          Novo Evento
        </Link>
      </div>

      {erro && <div className="error-msg">{erro}</div>}

      <div className="card">
        {carregando ? (
          <p>Carregando...</p>
        ) : eventos.length === 0 ? (
          <p>Nenhum evento cadastrado.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Nome</th>
                <th>Local</th>
                <th>Data do evento</th>
                <th>Abertura das vendas</th>
                <th>Acoes</th>
              </tr>
            </thead>
            <tbody>
              {eventos.map((evento) => (
                <tr key={evento.id}>
                  <td>{evento.nome}</td>
                  <td>{evento.local}</td>
                  <td>{formatarData(evento.data_hora_evento)}</td>
                  <td>{formatarData(evento.data_abertura_vendas)}</td>
                  <td className="actions">
                    <Link className="btn btn-secondary" to={`/eventos/${evento.id}/editar`}>
                      Editar
                    </Link>
                    <button className="btn btn-danger" onClick={() => excluir(evento.id)}>
                      Excluir
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default EventosList;
