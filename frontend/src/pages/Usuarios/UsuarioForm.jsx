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

  const [carregando, setCarregando] = useState(editando);
  const [falhaCarga, setFalhaCarga] = useState(false);

  useEffect(() => {
    async function carregarDados() {
      setErro("");
      setFalhaCarga(false);
      if (!id) {
        setForm(ESTADO_INICIAL);
        setCarregando(false);
        return;
      }
      setCarregando(true);
      try {
        const usuario = await buscarUsuario(id);
        setForm({
          nome: usuario.nome || "",
          email: usuario.email || "",
          cpf: usuario.cpf || "",
          telefone: usuario.telefone || "",
          senha: "",
        });
      } catch (erro) {
        setFalhaCarga(true);
        setErro(erro.response?.data?.erro || "Não foi possível carregar os dados.");
      } finally {
        setCarregando(false);
      }
    }
    carregarDados();
  }, [id]);

  function alterarCampo(evento) {
    const campo = evento.target.name;
    const valor = evento.target.value;
    setForm({ ...form, [campo]: valor });
  }

  async function salvar(evento) {
    evento.preventDefault();
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
  }

  return (
    <div className="card">
      <h2>{editando ? "Editar Usuario" : "Novo Usuario"}</h2>

      {erro && <div className="error-msg">{erro}</div>}

      <form onSubmit={salvar}>
        <div className="form-group">
          <label>Nome</label>
          <input value={form.nome} name="nome" onChange={alterarCampo} required />
        </div>

        <div className="form-group">
          <label>Email</label>
          <input type="email" value={form.email} name="email" onChange={alterarCampo} required />
        </div>

        <div className="form-group">
          <label>CPF (somente numeros)</label>
          <input
            value={form.cpf}
            name="cpf" onChange={alterarCampo}
            maxLength={11}
            required
          />
        </div>

        <div className="form-group">
          <label>Telefone</label>
          <input value={form.telefone} name="telefone" onChange={alterarCampo} />
        </div>

        <div className="form-group">
          <label>{editando ? "Nova senha (deixe em branco para manter)" : "Senha"}</label>
          <input
            type="password"
            value={form.senha}
            name="senha" onChange={alterarCampo}
            required={!editando}
          />
        </div>

        <div className="actions">
          <button className="btn btn-primary" type="submit" disabled={salvando || carregando || falhaCarga}>
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
