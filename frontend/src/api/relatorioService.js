import api from "./axiosConfig";

export async function obterRelatorioEventos() {
  const resposta = await api.get("/relatorios/eventos");
  return resposta.data;
}
