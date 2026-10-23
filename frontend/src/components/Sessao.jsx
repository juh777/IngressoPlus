import { createContext, useContext, useEffect, useState } from "react";
import { Navigate, useLocation } from "react-router-dom";
import api from "../api/axiosConfig";

const ContextoSessao = createContext(null);

export function ProvedorSessao({ children }) {
  const [usuario, setUsuario] = useState(null);
  const [carregando, setCarregando] = useState(true);
  useEffect(() => {
    api.get("/auth/sessao").then(resposta => setUsuario(resposta.data))
      .catch(() => setUsuario(null)).finally(() => setCarregando(false));
  }, []);
  async function sair() {
    await api.post("/auth/logout");
    setUsuario(null);
  }
  return <ContextoSessao.Provider value={{ usuario, setUsuario, carregando, sair }}>{children}</ContextoSessao.Provider>;
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
