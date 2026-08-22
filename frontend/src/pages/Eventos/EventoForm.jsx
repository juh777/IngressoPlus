import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { atualizarEvento, buscarEvento, criarEvento } from "../../api/eventoService";

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

  useEffect(() => {
    if (!editando) return;
    buscarEvento(id).then((evento) =>
      setForm({
        nome: evento.nome || "",
        descricao: evento.descricao || "",
        local: evento.local || "",
        categoria: evento.categoria || "",
        imagem_url: evento.imagem_url || "",
        data_hora_evento: evento.data_hora_evento ? evento.data_hora_evento.slice(0, 16) : "",
        data_abertura_vendas: evento.data_abertura_vendas
          ? evento.data_abertura_vendas.slice(0, 16)
          : "",
        ativo: evento.ativo === false ? "inativo" : "ativo",
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
        await atualizarEvento(id, { ...form, ativo: form.ativo === "ativo" });
      } else {
        const { ativo: _ativo, ...dados } = form;
        await criarEvento(dados);
      }
      navigate("/eventos");
    } catch (e) {
      setErro(e.response?.data?.erro || "Nao foi possivel salvar o evento.");
    } finally {
      setSalvando(false);
    }
  };

  return (
    <div className="card">
      <h2>{editando ? "Editar Evento" : "Novo Evento"}</h2>

      {erro && <div className="error-msg">{erro}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Nome</label>
          <input value={form.nome} onChange={handleChange("nome")} required />
        </div>

        <div className="form-group">
          <label>Descricao</label>
          <textarea value={form.descricao} onChange={handleChange("descricao")} rows={3} />
        </div>

        <div className="form-group">
          <label>Local</label>
          <input value={form.local} onChange={handleChange("local")} required />
        </div>

        <div className="form-group">
          <label>Categoria</label>
          <input value={form.categoria} onChange={handleChange("categoria")} />
        </div>

        <div className="form-group">
          <label>URL da imagem</label>
          <input value={form.imagem_url} onChange={handleChange("imagem_url")} />
        </div>

        <div className="form-group">
          <label>Data e hora do evento</label>
          <input
            type="datetime-local"
            value={form.data_hora_evento}
            onChange={handleChange("data_hora_evento")}
            required
          />
        </div>

        <div className="form-group">
          <label>Data e hora de abertura das vendas</label>
          <input
            type="datetime-local"
            value={form.data_abertura_vendas}
            onChange={handleChange("data_abertura_vendas")}
            required
          />
        </div>

        {editando && (
          <div className="form-group">
            <label>Status</label>
            <select value={form.ativo} onChange={handleChange("ativo")}>
              <option value="ativo">Ativo</option>
              <option value="inativo">Inativo</option>
            </select>
          </div>
        )}

        <div className="actions">
          <button className="btn btn-primary" type="submit" disabled={salvando}>
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
