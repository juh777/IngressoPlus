import api from "./axiosConfig";

export async function listarUsuarios() {
  const resposta = await api.get("/usuarios");
  return resposta.data;
}

export async function buscarUsuario(id) {
  const resposta = await api.get(`/usuarios/${id}`);
  return resposta.data;
}

export async function criarUsuario(dados) {
  const resposta = await api.post("/usuarios", dados);
  return resposta.data;
}

export async function atualizarUsuario(id, dados) {
  const resposta = await api.put(`/usuarios/${id}`, dados);
  return resposta.data;
}

export async function removerUsuario(id) {
  const resposta = await api.delete(`/usuarios/${id}`);
  return resposta.data;
}

export async function buscarUsuariosPorTermo(termo) {
  const resposta = await api.get("/usuarios/busca", { params: { termo } });
  return resposta.data;
}
