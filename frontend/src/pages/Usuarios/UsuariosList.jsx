import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { listarUsuarios, removerUsuario } from "../../api/usuarioService";

function formatarCpf(cpf) {
  if (!cpf || cpf.length !== 11) return cpf;
  return `${cpf.slice(0, 3)}.${cpf.slice(3, 6)}.${cpf.slice(6, 9)}-${cpf.slice(9)}`;
}

function UsuariosList() {
  const [usuarios, setUsuarios] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");

  const carregar = async () => {
    setCarregando(true);
    try {
      const dados = await listarUsuarios();
      setUsuarios(dados);
      setErro("");
    } catch (e) {
      setErro("Nao foi possivel carregar os usuarios.");
    } finally {
      setCarregando(false);
    }
  };

  useEffect(() => {
    carregar();
  }, []);

  const excluir = async (id) => {
    if (!window.confirm("Deseja realmente excluir este usuario?")) return;
    try {
      await removerUsuario(id);
      carregar();
    } catch (e) {
      setErro(e.response?.data?.erro || "Nao foi possivel excluir o usuario.");
    }
  };

  return (
    <div>
      <div className="card" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h2 style={{ margin: 0 }}>Usuarios</h2>
        <Link className="btn btn-primary" to="/usuarios/novo">
          Novo Usuario
        </Link>
      </div>

      {erro && <div className="error-msg">{erro}</div>}

      <div className="card">
        {carregando ? (
          <p>Carregando...</p>
        ) : usuarios.length === 0 ? (
          <p>Nenhum usuario cadastrado.</p>
        ) : (
          <table>
            <thead>
              <tr>
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
        )}
      </div>
    </div>
  );
}

export default UsuariosList;
