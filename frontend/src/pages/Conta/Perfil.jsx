import { useEffect, useState } from "react";
import api from "../../api/axiosConfig";
import { usarSessao } from "../../components/Sessao";
import Mensagens, { mensagemErro, dataHora } from "../../components/Mensagens";

export default function Perfil() {
  const { usuario, setUsuario } = usarSessao();
  const [form, setForm] = useState({ nome: usuario.nome, email: usuario.email, cpf: usuario.cpf, telefone: usuario.telefone || "", senha: "" });
  const [cofre, setCofre] = useState({ consentimento: false, endereco: "", cidade: "", preferencias: "" });
  const [erro, setErro] = useState(""); const [sucesso, setSucesso] = useState("");
  const [ocupado, setOcupado] = useState(false); const [historico, setHistorico] = useState([]);
  useEffect(() => { api.get("/perfil/cofre").then(r => setCofre(r.data)).catch(e => setErro(mensagemErro(e))); }, []);
  async function salvar(evento) {
    evento.preventDefault(); setOcupado(true); setErro(""); setSucesso("");
    try { const dados = { ...form }; if (!dados.senha) delete dados.senha;
      const resposta = await api.put("/perfil", dados); setUsuario(resposta.data);
      setForm({ ...form, senha: "" }); setSucesso("Perfil atualizado.");
    } catch (e) { setErro(mensagemErro(e)); } finally { setOcupado(false); }
  }
  async function salvarCofre(evento) {
    evento.preventDefault(); setOcupado(true); setErro(""); setSucesso("");
    try { const resposta = await api.put("/perfil/cofre", cofre); setCofre(resposta.data);
      setSucesso(cofre.consentimento ? "Dados protegidos salvos no cofre." : "Consentimento revogado. Os dados do cofre foram removidos.");
    } catch (e) { setErro(mensagemErro(e)); } finally { setOcupado(false); }
  }
  async function exportar() {
    setErro(""); setOcupado(true);
    try { const resposta = await api.get("/perfil/exportar"); setHistorico(resposta.data.historico);
      const arquivo = new Blob([JSON.stringify(resposta.data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(arquivo); const link = document.createElement("a"); link.href = url;
      link.download = "meus-dados-ingressoplus.json"; link.click(); URL.revokeObjectURL(url);
      setSucesso("Arquivo dos seus dados exportado.");
    } catch (e) { setErro(mensagemErro(e)); } finally { setOcupado(false); }
  }
  return <><div className="page-title"><span className="eyebrow">MINHA CONTA</span><h1>Perfil e privacidade</h1></div>
    <Mensagens erro={erro} sucesso={sucesso} /><div className="two-columns">
      <section className="card"><h2>Dados pessoais</h2><form onSubmit={salvar}>
        {[["nome", "Nome"], ["email", "E-mail"], ["cpf", "CPF"], ["telefone", "Telefone"]].map(([campo, titulo]) =>
          <label className="form-group" key={campo}>{titulo}<input name={campo} type={campo === "email" ? "email" : "text"} value={form[campo]}
            required={campo !== "telefone"} onChange={e => setForm({ ...form, [campo]: e.target.value })} /></label>)}
        <label className="form-group">Nova senha (opcional)<input type="password" value={form.senha} minLength={6} onChange={e => setForm({ ...form, senha: e.target.value })} autoComplete="new-password" /></label>
        <button className="btn btn-primary" disabled={ocupado}>Salvar perfil</button></form></section>
      <section className="card"><h2>Cofre de dados</h2><p className="muted">Os campos abaixo são criptografados no banco. Nunca armazene dados de cartão.</p>
        <form onSubmit={salvarCofre}><label className="check-label"><input type="checkbox" checked={cofre.consentimento} onChange={e => setCofre({ ...cofre, consentimento: e.target.checked })} /> Autorizo salvar estes dados e usar minhas preferências nas recomendações.</label>
          {[["endereco", "Endereço"], ["cidade", "Cidade"], ["preferencias", "Categorias de interesse (ex.: Música, Teatro)"]].map(([campo, titulo]) =>
            <label className="form-group" key={campo}>{titulo}<input value={cofre[campo]} maxLength={300} disabled={!cofre.consentimento} onChange={e => setCofre({ ...cofre, [campo]: e.target.value })} /></label>)}
          <button className="btn btn-primary" disabled={ocupado}>Salvar consentimento e cofre</button></form></section>
    </div><section className="card"><h2>Seus dados, sob seu controle</h2><p>Exporte seu perfil, cofre, compras, documentos, grupos, alertas e histórico de ações.</p>
      <button className="btn btn-secondary" onClick={exportar} disabled={ocupado}>Exportar meus dados em JSON</button>
      {historico.length > 0 && <ul>{historico.slice(0, 10).map((item, indice) => <li key={indice}>{dataHora(item.criado_em)} — {item.acao}</li>)}</ul>}
      <p className="muted small">Controles de privacidade de um projeto acadêmico; não representam certificação LGPD ou PCI-DSS.</p></section></>;
}
