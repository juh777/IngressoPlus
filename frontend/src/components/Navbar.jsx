import { useRef, useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { usarSessao } from "./Sessao";
import "./Navbar.css";

export default function Navbar() {
  const { usuario, sair, temAlertasNaoLidos } = usarSessao(); const navigate = useNavigate();
  const modalSaida = useRef(null);
  const saidaPendente = useRef(false);
  const [encerrando, setEncerrando] = useState(false);
  const [erroSaida, setErroSaida] = useState("");
  function confirmarSaida() { setErroSaida(""); modalSaida.current.showModal(); }
  async function encerrar() {
    if (saidaPendente.current) return;
    saidaPendente.current = true;
    setEncerrando(true); setErroSaida("");
    try { await sair(); modalSaida.current.close(); navigate("/eventos"); }
    catch { setErroSaida("Não foi possível sair. Tente novamente."); }
    finally { saidaPendente.current = false; setEncerrando(false); }
  }
  return <header className="navbar"><div className="navbar-inner"><NavLink className="navbar-brand" to="/eventos"><img src="/logo-ingresso-plus.png" alt="Ingresso+" width="180" height="40" /></NavLink>
    <nav className="navbar-links" aria-label="Navegação principal"><NavLink to="/eventos">Eventos</NavLink>
      {usuario && <><NavLink to="/meus-ingressos">Meus ingressos</NavLink><NavLink to="/grupos">Grupos</NavLink><NavLink className="nav-alerts" to="/alertas" aria-label={temAlertasNaoLidos ? "Alertas: há notificações não lidas" : "Alertas"}>Alertas{temAlertasNaoLidos && <span className="notification-dot" aria-hidden="true" />}</NavLink><NavLink to="/meia-entrada">Meia-entrada</NavLink><NavLink to="/perfil">Perfil</NavLink></>}
      {usuario?.papel === "admin" && <><NavLink to="/usuarios">Usuários</NavLink><NavLink to="/relatorios/vendas">Vendas</NavLink><NavLink to="/relatorios" end>Relatórios</NavLink></>}
      {usuario ? <button className="nav-exit" onClick={confirmarSaida}>Sair</button> : <><NavLink to="/login">Entrar</NavLink><NavLink to="/cadastro">Criar conta</NavLink></>}
    </nav></div>
    <dialog ref={modalSaida} className="logout-dialog" aria-labelledby="logout-title" aria-describedby="logout-description" aria-busy={encerrando}
      onCancel={evento => { if (encerrando) evento.preventDefault(); }}>
      <h2 id="logout-title">Sair da conta?</h2>
      <p id="logout-description" className="logout-description">Você precisará entrar novamente para acessar seus ingressos e reservas.</p>
      {erroSaida && <div className="error-msg" role="alert">{erroSaida}</div>}
      <div className="actions">
        <button type="button" className="btn btn-secondary" autoFocus disabled={encerrando} onClick={() => modalSaida.current.close()}>Cancelar</button>
        <button type="button" className="btn btn-primary" disabled={encerrando} onClick={encerrar}>{encerrando ? "Saindo…" : "Sair da conta"}</button>
      </div>
    </dialog></header>;
}
