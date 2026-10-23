import { usarSessao } from "../../components/Sessao";
import Recomendacoes from "../../components/Recomendacoes";
import { dataHora } from "../../components/Mensagens";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { filtrarEventos, listarEventos, removerEvento } from "../../api/eventoService";

function formatarData(iso) {
  if (!iso) return "-";
  return dataHora(iso);
}

const FILTROS_INICIAIS = { categoria: "", local: "", status: "" };

function descricaoStatus(evento) {
  return evento.ativo ? "Ativo" : "Inativo";
}

function EventosList() {
  const { usuario } = usarSessao();
  const admin = usuario?.papel === "admin";
  const [eventos, setEventos] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");
  const [filtros, setFiltros] = useState(FILTROS_INICIAIS);
  const [filtroAtivo, setFiltroAtivo] = useState(false);

  async function carregar(filtrosAplicados = null) {
    setCarregando(true);
    try {
      const dados = filtrosAplicados ? await filtrarEventos(filtrosAplicados) : await listarEventos();
      setEventos(dados);
      setErro("");
    } catch (e) {
      setErro("Nao foi possivel carregar os eventos.");
    } finally {
      setCarregando(false);
    }
  }

  useEffect(() => {
    carregar();
  }, []);

  function alterarFiltro(evento) {
    const campo = evento.target.name;
    setFiltros({ ...filtros, [campo]: evento.target.value });
  }

  async function aplicarFiltros(e) {
    e.preventDefault();
    setFiltroAtivo(true);
    await carregar(filtros);
  }

  function limparFiltros() {
    setFiltros(FILTROS_INICIAIS);
    setFiltroAtivo(false);
    carregar();
  }

  async function excluir(id) {
    if (!window.confirm("Deseja realmente excluir este evento?")) return;
    try {
      await removerEvento(id);
      carregar(filtroAtivo ? filtros : null);
    } catch (e) {
      setErro(e.response?.data?.erro || "Nao foi possivel excluir o evento.");
    }
  }

  return (
    <div>
      <div className="card page-header">
        <h2>Eventos</h2>
        {admin && <Link className="btn btn-primary" to="/eventos/novo">
          Novo Evento
        </Link>}
      </div>

      <Recomendacoes />

      {erro && <div className="error-msg">{erro}</div>}

      <div className="card">
        <form className="filter-form event-filter-form" onSubmit={aplicarFiltros}>
          <div className="filter-field">
            <label htmlFor="filtro-categoria">Categoria</label>
            <input
              id="filtro-categoria"
              value={filtros.categoria}
              name="categoria" onChange={alterarFiltro}
              placeholder="Ex.: Show"
              disabled={carregando}
            />
          </div>
          <div className="filter-field">
            <label htmlFor="filtro-local">Local</label>
            <input
              id="filtro-local"
              value={filtros.local}
              name="local" onChange={alterarFiltro}
              placeholder="Ex.: Sao Paulo"
              disabled={carregando}
            />
          </div>
          <div className="filter-field">
            <label htmlFor="filtro-status">Status</label>
            <select
              id="filtro-status"
              value={filtros.status}
              name="status" onChange={alterarFiltro}
              disabled={carregando}
            >
              <option value="">Todos</option>
              <option value="ativo">Ativos</option>
              <option value="inativo">Inativos</option>
            </select>
          </div>
          <div className="filter-actions">
            <button className="btn btn-primary" type="submit" disabled={carregando}>
              {carregando && filtroAtivo ? "Filtrando..." : "Filtrar"}
            </button>
            <button
              className="btn btn-secondary"
              type="button"
              onClick={limparFiltros}
              disabled={
                carregando ||
                (!filtros.categoria && !filtros.local && !filtros.status && !filtroAtivo)
              }
            >
              Limpar
            </button>
          </div>
        </form>

        {carregando ? (
          <p>Carregando...</p>
        ) : eventos.length === 0 ? (
          <p>{filtroAtivo ? "Nenhum evento encontrado para os filtros informados." : "Nenhum evento cadastrado."}</p>
        ) : (
          <div className="table-responsive">
            <table>
              <thead>
                <tr>
                  <th scope="col">ID</th>
                  <th>Nome</th>
                  <th>Categoria</th>
                  <th>Local</th>
                  <th>Status</th>
                  <th>Data do evento</th>
                  <th>Abertura das vendas</th>
                  <th>Acoes</th>
                </tr>
              </thead>
              <tbody>
                {eventos.map((evento) => (
                  <tr key={evento.id}>
                    <td>{evento.id}</td>
                    <td>{evento.nome}</td>
                    <td>{evento.categoria || "-"}</td>
                    <td>{evento.local}</td>
                    <td>
                      <span className={`status-badge ${descricaoStatus(evento) === "Ativo" ? "active" : "inactive"}`}>
                        {descricaoStatus(evento)}
                      </span>
                    </td>
                    <td>{formatarData(evento.data_hora_evento)}</td>
                    <td>{formatarData(evento.data_abertura_vendas)}</td>
                    <td className="actions">
                      <Link className="btn btn-primary" to={`/eventos/${evento.id}`}>Ver ingressos</Link>
                      {admin && <>
                      <Link className="btn btn-secondary" to={`/eventos/${evento.id}/editar`}>
                        Editar
                      </Link>
                      <button className="btn btn-danger" onClick={() => excluir(evento.id)}>
                        Excluir
                      </button></>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default EventosList;
