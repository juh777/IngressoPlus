import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import {
  buscarUsuariosPorTermo,
  listarUsuarios,
  removerUsuario,
} from "../../api/usuarioService";

function formatarCpf(cpf) {
  if (!cpf || cpf.length !== 11) return cpf;
  return `${cpf.slice(0, 3)}.${cpf.slice(3, 6)}.${cpf.slice(6, 9)}-${cpf.slice(9)}`;
}

function UsuariosList() {
  const [usuarios, setUsuarios] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");
  const [termo, setTermo] = useState("");
  const [buscaAtiva, setBuscaAtiva] = useState(false);

  async function carregar(termoBusca = "") {
    setCarregando(true);
    try {
      const dados = termoBusca.trim()
        ? await buscarUsuariosPorTermo(termoBusca.trim())
        : await listarUsuarios();
      setUsuarios(dados);
      setErro("");
    } catch (e) {
      setErro("Nao foi possivel carregar os usuarios.");
    } finally {
      setCarregando(false);
    }
  }

  useEffect(() => {
    carregar();
  }, []);

  async function buscar(e) {
    e.preventDefault();
    const termoNormalizado = termo.trim();
    setBuscaAtiva(Boolean(termoNormalizado));
    await carregar(termoNormalizado);
  }

  function limparBusca() {
    setTermo("");
    setBuscaAtiva(false);
    carregar();
  }

  async function excluir(id) {
    if (!window.confirm("Deseja realmente excluir este usuario?")) return;
    try {
      await removerUsuario(id);
      carregar(buscaAtiva ? termo : "");
    } catch (e) {
      setErro(e.response?.data?.erro || "Nao foi possivel excluir o usuario.");
    }
  }

  return (
    <div>
      <div className="card page-header">
        <h2>Usuarios</h2>
        <Link className="btn btn-primary" to="/usuarios/novo">
          Novo Usuario
        </Link>
      </div>

      {erro && <div className="error-msg">{erro}</div>}

      <div className="card">
        <form className="filter-form" onSubmit={buscar}>
          <div className="filter-field">
            <label htmlFor="busca-usuario">Buscar por nome ou e-mail</label>
            <input
              id="busca-usuario"
              type="search"
              value={termo}
              onChange={(e) => setTermo(e.target.value)}
              placeholder="Ex.: Ana ou ana@email.com"
              disabled={carregando}
            />
          </div>
          <div className="filter-actions">
            <button className="btn btn-primary" type="submit" disabled={carregando}>
              {carregando && buscaAtiva ? "Buscando..." : "Buscar"}
            </button>
            <button
              className="btn btn-secondary"
              type="button"
              onClick={limparBusca}
              disabled={carregando || (!termo && !buscaAtiva)}
            >
              Limpar
            </button>
          </div>
        </form>

        {carregando ? (
          <p>Carregando...</p>
        ) : usuarios.length === 0 ? (
          <p>{buscaAtiva ? "Nenhum usuario encontrado para esta busca." : "Nenhum usuario cadastrado."}</p>
        ) : (
          <div className="table-responsive">
            <table>
              <thead>
                <tr>
                  <th scope="col">ID</th>
                  <th>Nome</th>
                  <th>Email</th>
                  <th>CPF</th>
                  <th>Telefone</th>
                  <th>Acoes</th>
                </tr>
              </thead>
              <tbody>
                {usuarios.map((usuario) => (
                  <tr key={usuario.id}>
                    <td>{usuario.id}</td>
                    <td>{usuario.nome}</td>
                    <td>{usuario.email}</td>
                    <td>{formatarCpf(usuario.cpf)}</td>
                    <td>{usuario.telefone || "-"}</td>
                    <td className="actions">
                      <Link className="btn btn-secondary" to={`/usuarios/${usuario.id}/editar`}>
                        Editar
                      </Link>
                      <button className="btn btn-danger" onClick={() => excluir(usuario.id)}>
                        Excluir
                      </button>
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

export default UsuariosList;
