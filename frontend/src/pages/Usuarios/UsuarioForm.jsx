import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { atualizarUsuario, buscarUsuario, criarUsuario } from "../../api/usuarioService";

const ESTADO_INICIAL = {
  nome: "",
  email: "",
  cpf: "",
  telefone: "",
  senha: "",
};

function UsuarioForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const editando = Boolean(id);

  const [form, setForm] = useState(ESTADO_INICIAL);
  const [erro, setErro] = useState("");
  const [salvando, setSalvando] = useState(false);

  useEffect(() => {
    if (!editando) return;
    buscarUsuario(id).then((usuario) =>
      setForm({
        nome: usuario.nome || "",
        email: usuario.email || "",
        cpf: usuario.cpf || "",
        telefone: usuario.telefone || "",
        senha: "",
      })
    );
  }, [editando, id]);

  const handleChange = (campo) => (e) =>
    setForm((atual) => ({ ...atual, [campo]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSalvando(true);
    setErro("");
    try {
      if (editando) {
        const dados = { ...form };
        if (!dados.senha) delete dados.senha;
        await atualizarUsuario(id, dados);
      } else {
        await criarUsuario(form);
      }
      navigate("/usuarios");
    } catch (e) {
      setErro(e.response?.data?.erro || "Nao foi possivel salvar o usuario.");
    } finally {
      setSalvando(false);
    }
  };

  return (
    <div className="card">
      <h2>{editando ? "Editar Usuario" : "Novo Usuario"}</h2>

      {erro && <div className="error-msg">{erro}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Nome</label>
          <input value={form.nome} onChange={handleChange("nome")} required />
        </div>

        <div className="form-group">
          <label>Email</label>
          <input type="email" value={form.email} onChange={handleChange("email")} required />
        </div>

        <div className="form-group">
          <label>CPF (somente numeros)</label>
          <input
            value={form.cpf}
            onChange={handleChange("cpf")}
            maxLength={11}
            required
          />
        </div>

        <div className="form-group">
          <label>Telefone</label>
          <input value={form.telefone} onChange={handleChange("telefone")} />
        </div>

        <div className="form-group">
          <label>{editando ? "Nova senha (deixe em branco para manter)" : "Senha"}</label>
          <input
            type="password"
            value={form.senha}
            onChange={handleChange("senha")}
            required={!editando}
          />
        </div>

        <div className="actions">
          <button className="btn btn-primary" type="submit" disabled={salvando}>
            {salvando ? "Salvando..." : "Salvar"}
          </button>
          <button className="btn btn-secondary" type="button" onClick={() => navigate("/usuarios")}>
            Cancelar
          </button>
        </div>
      </form>
    </div>
  );
}

export default UsuarioForm;
