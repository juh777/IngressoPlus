import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { atualizarEvento, buscarEvento, criarEvento } from "../../api/eventoService";
import { dataParaFormulario } from "../../components/Mensagens";

const ESTADO_INICIAL = {
  nome: "",
  descricao: "",
  local: "",
  categoria: "",
  imagem_url: "",
  data_hora_evento: "",
  data_abertura_vendas: "",
  ativo: "ativo",
};

function EventoForm() {
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
        const evento = await buscarEvento(id);
        setForm({
          nome: evento.nome || "",
          descricao: evento.descricao || "",
          local: evento.local || "",
          categoria: evento.categoria || "",
          imagem_url: evento.imagem_url || "",
          data_hora_evento: dataParaFormulario(evento.data_hora_evento),
          data_abertura_vendas: dataParaFormulario(evento.data_abertura_vendas),
          ativo: evento.ativo ? "ativo" : "inativo",
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
      const dados = { ...form, data_hora_evento: new Date(form.data_hora_evento).toISOString(),
        data_abertura_vendas: new Date(form.data_abertura_vendas).toISOString() };
      if (editando) {
        await atualizarEvento(id, { ...dados, ativo: form.ativo === "ativo" });
      } else {
        delete dados.ativo;
        await criarEvento(dados);
      }
      navigate("/eventos");
    } catch (e) {
      setErro(e.response?.data?.erro || "Nao foi possivel salvar o evento.");
    } finally {
      setSalvando(false);
    }
  }

  return (
    <div className="card">
      <h2>{editando ? "Editar Evento" : "Novo Evento"}</h2>

      {erro && <div className="error-msg">{erro}</div>}

      <form onSubmit={salvar}>
        <div className="form-group">
          <label>Nome</label>
          <input value={form.nome} name="nome" onChange={alterarCampo} required />
        </div>

        <div className="form-group">
          <label>Descricao</label>
          <textarea value={form.descricao} name="descricao" onChange={alterarCampo} rows={3} />
        </div>

        <div className="form-group">
          <label>Local</label>
          <input value={form.local} name="local" onChange={alterarCampo} required />
        </div>

        <div className="form-group">
          <label>Categoria</label>
          <input value={form.categoria} name="categoria" onChange={alterarCampo} />
        </div>

        <div className="form-group">
          <label>URL da imagem</label>
          <input value={form.imagem_url} name="imagem_url" onChange={alterarCampo} />
        </div>

        <div className="form-group">
          <label>Data e hora do evento</label>
          <input
            type="datetime-local"
            value={form.data_hora_evento}
            name="data_hora_evento" onChange={alterarCampo}
            required
          />
        </div>

        <div className="form-group">
          <label>Data e hora de abertura das vendas</label>
          <input
            type="datetime-local"
            value={form.data_abertura_vendas}
            name="data_abertura_vendas" onChange={alterarCampo}
            required
          />
        </div>

        {editando && (
          <div className="form-group">
            <label>Status</label>
            <select value={form.ativo} name="ativo" onChange={alterarCampo}>
              <option value="ativo">Ativo</option>
              <option value="inativo">Inativo</option>
            </select>
          </div>
        )}

        <div className="actions">
          <button className="btn btn-primary" type="submit" disabled={salvando || carregando || falhaCarga}>
            {salvando ? "Salvando..." : "Salvar"}
          </button>
          <button className="btn btn-secondary" type="button" onClick={() => navigate("/eventos")}>
            Cancelar
          </button>
        </div>
      </form>
    </div>
  );
}

export default EventoForm;
