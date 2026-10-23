import { ProvedorSessao, RotaProtegida } from './components/Sessao';
import Login from './pages/Conta/Login';
import Perfil from './pages/Conta/Perfil';
import MeiaEntrada from './pages/Conta/MeiaEntrada';
import EventoDetalhe from './pages/Eventos/EventoDetalhe';
import MeusIngressos from './pages/Ingressos/MeusIngressos';
import Grupos from './pages/Grupos/Grupos';
import Alertas from './pages/Notificacoes/Alertas';
import Vendas from './pages/Relatorios/Vendas';
import { Navigate, Route, Routes } from "react-router-dom";

import Navbar from "./components/Navbar.jsx";
import EventosList from "./pages/Eventos/EventosList.jsx";
import EventoForm from "./pages/Eventos/EventoForm.jsx";
import UsuariosList from "./pages/Usuarios/UsuariosList.jsx";
import UsuarioForm from "./pages/Usuarios/UsuarioForm.jsx";
import RelatorioEventos from "./pages/Relatorios/RelatorioEventos.jsx";

function App() {
  return (
    <ProvedorSessao>
      <Navbar />
      <main className="container">
        <Routes>
          <Route path="/" element={<Navigate to="/eventos" replace />} />
          <Route path="/eventos" element={<EventosList />} />
          <Route path="/eventos/novo" element={<RotaProtegida admin><EventoForm /></RotaProtegida>} />
          <Route path="/eventos/:id/editar" element={<RotaProtegida admin><EventoForm /></RotaProtegida>} />
          <Route path="/usuarios" element={<RotaProtegida admin><UsuariosList /></RotaProtegida>} />
          <Route path="/usuarios/novo" element={<RotaProtegida admin><UsuarioForm /></RotaProtegida>} />
          <Route path="/usuarios/:id/editar" element={<RotaProtegida admin><UsuarioForm /></RotaProtegida>} />
          <Route path="/relatorios" element={<RotaProtegida admin><RelatorioEventos /></RotaProtegida>} />
          <Route path="/login" element={<Login />} />
          <Route path="/cadastro" element={<Login cadastro />} />
          <Route path="/eventos/:id" element={<EventoDetalhe />} />
          <Route path="/perfil" element={<RotaProtegida><Perfil /></RotaProtegida>} />
          <Route path="/meia-entrada" element={<RotaProtegida><MeiaEntrada /></RotaProtegida>} />
          <Route path="/meus-ingressos" element={<RotaProtegida><MeusIngressos /></RotaProtegida>} />
          <Route path="/grupos" element={<RotaProtegida><Grupos /></RotaProtegida>} />
          <Route path="/alertas" element={<RotaProtegida><Alertas /></RotaProtegida>} />
          <Route path="/relatorios/vendas" element={<RotaProtegida admin><Vendas /></RotaProtegida>} />
          <Route path="*" element={<div className="card"><h2>Página não encontrada</h2><a href="/eventos">Voltar aos eventos</a></div>} />
        </Routes>
      </main>
    </ProvedorSessao>
  );
}

export default App;
