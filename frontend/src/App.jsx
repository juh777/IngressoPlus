import { Navigate, Route, Routes } from "react-router-dom";

import Navbar from "./components/Navbar.jsx";
import EventosList from "./pages/Eventos/EventosList.jsx";
import EventoForm from "./pages/Eventos/EventoForm.jsx";
import UsuariosList from "./pages/Usuarios/UsuariosList.jsx";
import UsuarioForm from "./pages/Usuarios/UsuarioForm.jsx";
import RelatorioEventos from "./pages/Relatorios/RelatorioEventos.jsx";

function App() {
  return (
    <>
      <Navbar />
      <main className="container">
        <Routes>
          <Route path="/" element={<Navigate to="/eventos" replace />} />
          <Route path="/eventos" element={<EventosList />} />
          <Route path="/eventos/novo" element={<EventoForm />} />
          <Route path="/eventos/:id/editar" element={<EventoForm />} />
          <Route path="/usuarios" element={<UsuariosList />} />
          <Route path="/usuarios/novo" element={<UsuarioForm />} />
          <Route path="/usuarios/:id/editar" element={<UsuarioForm />} />
          <Route path="/relatorios" element={<RelatorioEventos />} />
        </Routes>
      </main>
    </>
  );
}

export default App;
