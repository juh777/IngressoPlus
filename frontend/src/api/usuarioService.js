import api from "./axiosConfig";

export const listarUsuarios = () => api.get("/usuarios").then((res) => res.data);

export const buscarUsuariosPorTermo = (termo) =>
  api
    .get("/usuarios/busca", { params: { termo } })
    .then((res) => res.data);

export const buscarUsuario = (id) => api.get(`/usuarios/${id}`).then((res) => res.data);

export const criarUsuario = (dados) => api.post("/usuarios", dados).then((res) => res.data);

export const atualizarUsuario = (id, dados) =>
  api.put(`/usuarios/${id}`, dados).then((res) => res.data);

export const removerUsuario = (id) => api.delete(`/usuarios/${id}`);
