import api from "./axiosConfig";

export const listarEventos = () => api.get("/eventos").then((res) => res.data);

export const buscarEvento = (id) => api.get(`/eventos/${id}`).then((res) => res.data);

export const criarEvento = (dados) => api.post("/eventos", dados).then((res) => res.data);

export const atualizarEvento = (id, dados) =>
  api.put(`/eventos/${id}`, dados).then((res) => res.data);

export const removerEvento = (id) => api.delete(`/eventos/${id}`);
