export function mensagemErro(erro) {
  return erro.response?.data?.erro || "Não foi possível concluir. Verifique a conexão e tente novamente.";
}

export default function Mensagens({ erro, sucesso }) {
  return <>{erro && <div className="error-msg" role="alert">{erro}</div>}
    {sucesso && <div className="success-msg" role="status">{sucesso}</div>}</>;
}

export function moeda(valor) {
  return Number(valor || 0).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

export function dataHora(valor) {
  if (!valor) return "—";
  // As datas da API são UTC. O navegador exibe no fuso local.
  return new Date(valor.includes("T") && !/[Z+]$/.test(valor) ? valor + "Z" : valor).toLocaleString("pt-BR");
}

export function dataParaFormulario(valor) {
  const data = new Date(valor + "Z");
  const local = new Date(data.getTime() - data.getTimezoneOffset() * 60000);
  return local.toISOString().slice(0, 16);
}
