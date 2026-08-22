import api from "./axiosConfig";

export const obterRelatorioEventos = () =>
  api.get("/relatorios/eventos").then((res) => res.data);
