import { NavLink, useNavigate } from "react-router-dom";
import { usarSessao } from "./Sessao";
import "./Navbar.css";

export default function Navbar() {
  const { usuario, sair } = usarSessao(); const navigate = useNavigate();
  async function encerrar() { try { await sair(); navigate("/eventos"); } catch { window.alert("Não foi possível sair. Tente novamente."); } }
  return <header className="navbar"><div className="navbar-inner"><NavLink className="navbar-brand" to="/eventos">Ingresso<span>+</span></NavLink>
    <nav className="navbar-links" aria-label="Navegação principal"><NavLink to="/eventos">Eventos</NavLink>
      {usuario && <><NavLink to="/meus-ingressos">Meus ingressos</NavLink><NavLink to="/grupos">Grupos</NavLink><NavLink to="/alertas">Alertas</NavLink><NavLink to="/meia-entrada">Meia-entrada</NavLink><NavLink to="/perfil">Perfil</NavLink></>}
      {usuario?.papel === "admin" && <><NavLink to="/usuarios">Usuários</NavLink><NavLink to="/relatorios/vendas">Vendas</NavLink><NavLink to="/relatorios" end>Relatórios</NavLink></>}
      {usuario ? <button className="nav-exit" onClick={encerrar}>Sair</button> : <><NavLink to="/login">Entrar</NavLink><NavLink to="/cadastro">Criar conta</NavLink></>}
    </nav></div><div className="demo-bar">DEMONSTRAÇÃO ACADÊMICA · compras e estornos sem cobrança real</div></header>;
}
