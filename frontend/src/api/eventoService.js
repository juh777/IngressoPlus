import api from "./axiosConfig";

export async function listarEventos() {
  const resposta = await api.get("/eventos");
  return resposta.data;
}

export async function buscarEvento(id) {
  const resposta = await api.get(`/eventos/${id}`);
  return resposta.data;
}

export async function criarEvento(dados) {
  const resposta = await api.post("/eventos", dados);
  return resposta.data;
}

export async function atualizarEvento(id, dados) {
  const resposta = await api.put(`/eventos/${id}`, dados);
  return resposta.data;
}

export async function removerEvento(id) {
  const resposta = await api.delete(`/eventos/${id}`);
  return resposta.data;
}

export async function filtrarEventos(filtros) {
  const resposta = await api.get("/eventos/filtro", { params: filtros });
  return resposta.data;
}
