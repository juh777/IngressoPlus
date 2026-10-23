import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import api from "../../api/axiosConfig";
import { usarSessao } from "../../components/Sessao";
import Mensagens, { mensagemErro } from "../../components/Mensagens";

export default function Login({ cadastro = false }) {
  const [form, setForm] = useState({ nome: "", email: "", cpf: "", telefone: "", senha: "" });
  const [erro, setErro] = useState("");
  const [ocupado, setOcupado] = useState(false);
  const { setUsuario } = usarSessao();
  const navigate = useNavigate();
  const local = useLocation();
  function alterar(evento) { setForm({ ...form, [evento.target.name]: evento.target.value }); }
  async function enviar(evento) {
    evento.preventDefault(); setOcupado(true); setErro("");
    try {
      const resposta = await api.post(cadastro ? "/auth/cadastro" : "/auth/login", form);
      setUsuario(resposta.data);
      navigate(local.state?.voltar || "/eventos", { replace: true });
    } catch (erro) { setErro(mensagemErro(erro)); }
    finally { setOcupado(false); }
  }
  return <section className="card auth-card">
    <span className="eyebrow">SUA CONTA INGRESSO+</span><h1>{cadastro ? "Crie sua conta" : "Bem-vindo de volta"}</h1>
    <p className="muted">Reserve seu lugar, acompanhe seus ingressos e receba alertas de abertura.</p>
    <Mensagens erro={erro} />
    <form onSubmit={enviar}>
      {cadastro && <><label className="form-group">Nome<input name="nome" value={form.nome} onChange={alterar} maxLength={150} required autoComplete="name" /></label>
        <label className="form-group">CPF<input name="cpf" value={form.cpf} onChange={alterar} maxLength={14} required /></label>
        <label className="form-group">Telefone<input name="telefone" value={form.telefone} onChange={alterar} maxLength={20} autoComplete="tel" /></label></>}
      <label className="form-group">E-mail<input type="email" name="email" value={form.email} onChange={alterar} required autoComplete="email" /></label>
      <label className="form-group">Senha<input type="password" name="senha" value={form.senha} onChange={alterar} minLength={6} required autoComplete={cadastro ? "new-password" : "current-password"} /></label>
      <button className="btn btn-primary" disabled={ocupado}>{ocupado ? "Aguarde…" : cadastro ? "Criar conta" : "Entrar"}</button>
    </form><p>{cadastro ? "Já possui conta?" : "Ainda não tem conta?"} <Link to={cadastro ? "/login" : "/cadastro"}>{cadastro ? "Entrar" : "Cadastre-se"}</Link></p>
    <p className="demo-note">Ambiente acadêmico de demonstração. Os pagamentos são simulados.</p>
  </section>;
}
