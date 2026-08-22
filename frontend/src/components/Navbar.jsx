import { NavLink } from "react-router-dom";
import "./Navbar.css";

function Navbar() {
  return (
    <header className="navbar">
      <div className="navbar-inner">
        <span className="navbar-brand">Sistema de Ingressos</span>
        <nav className="navbar-links">
          <NavLink to="/eventos" className={({ isActive }) => (isActive ? "active" : "")}>
            Eventos
          </NavLink>
          <NavLink to="/usuarios" className={({ isActive }) => (isActive ? "active" : "")}>
            Usuarios
          </NavLink>
          <NavLink to="/relatorios" className={({ isActive }) => (isActive ? "active" : "")}>
            Relatórios
          </NavLink>
        </nav>
      </div>
    </header>
  );
}

export default Navbar;
