import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { Navigate, useLocation } from "react-router-dom";
import api from "../api/axiosConfig";

const ContextoSessao = createContext(null);

export function ProvedorSessao({ children }) {
  const [usuario, setUsuario] = useState(null);
  const [carregando, setCarregando] = useState(true);
  const [estadoAlertas, setEstadoAlertas] = useState({ usuarioId: null, itens: [] });
  const usuarioId = usuario?.id;
  const carregarAlertas = useCallback(async (signal) => {
    if (!usuarioId) return [];
    const { data } = await api.get("/alertas", { signal });
    if (!signal?.aborted) setEstadoAlertas({ usuarioId, itens: data });
    return data;
  }, [usuarioId]);
  const marcarAlertasLidos = useCallback(async (ids) => {
    await Promise.all(ids.map(id => api.put(`/alertas/${id}`, { acao: "ler" })));
    setEstadoAlertas(atual => atual.usuarioId === usuarioId
      ? { ...atual, itens: atual.itens.map(alerta => ids.includes(alerta.id) ? { ...alerta, lido: true } : alerta) }
      : atual);
  }, [usuarioId]);
  useEffect(() => {
    if (!usuarioId) return;
    const controller = new AbortController();
    const conferir = () => {
      if (document.visibilityState === "visible") carregarAlertas(controller.signal).catch(() => {});
    };
    conferir();
    const timer = setInterval(conferir, 10000);
    document.addEventListener("visibilitychange", conferir);
    return () => { controller.abort(); clearInterval(timer); document.removeEventListener("visibilitychange", conferir); };
  }, [usuarioId, carregarAlertas]);
  useEffect(() => {
    api.get("/auth/sessao").then(resposta => setUsuario(resposta.data))
      .catch(() => setUsuario(null)).finally(() => setCarregando(false));
  }, []);
  async function sair() {
    await api.post("/auth/logout");
    setUsuario(null);
  }
  const alertas = estadoAlertas.usuarioId === usuarioId ? estadoAlertas.itens : [];
  const temAlertasNaoLidos = alertas.some(alerta => alerta.status === "enviado" && !alerta.lido);
  return <ContextoSessao.Provider value={{ usuario, setUsuario, carregando, sair, alertas, temAlertasNaoLidos, carregarAlertas, marcarAlertasLidos }}>{children}</ContextoSessao.Provider>;
}

export function usarSessao() { return useContext(ContextoSessao); }

export function RotaProtegida({ children, admin = false }) {
  const { usuario, carregando } = usarSessao();
  const local = useLocation();
  if (carregando) return <p role="status">Carregando sua sessão…</p>;
  if (!usuario) return <Navigate to="/login" state={{ voltar: local.pathname }} replace />;
  if (admin && usuario.papel !== "admin") return <div className="card"><h2>Acesso restrito</h2><p>Esta área é exclusiva do administrador.</p></div>;
  return children;
}
