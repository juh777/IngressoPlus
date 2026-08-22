import { useEffect, useState } from "react";

import { obterRelatorioEventos } from "../../api/relatorioService";

function formatarNumero(valor) {
  return Number(valor || 0).toLocaleString("pt-BR");
}

function RelatorioEventos() {
  const [relatorio, setRelatorio] = useState(null);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");

  const carregarRelatorio = async () => {
    setCarregando(true);
    setErro("");

    try {
      const dados = await obterRelatorioEventos();
      setRelatorio(dados);
    } catch (e) {
      setRelatorio(null);
      setErro(e.response?.data?.erro || "Não foi possível carregar o relatório de eventos.");
    } finally {
      setCarregando(false);
    }
  };

  useEffect(() => {
    carregarRelatorio();
  }, []);

  const categorias = relatorio?.categorias || [];

  return (
    <section aria-labelledby="titulo-relatorio">
      <div className="card page-header report-header">
        <div>
          <h2 id="titulo-relatorio">Relatório de Eventos</h2>
          <p>Resumo dos eventos cadastrados e sua distribuição por categoria.</p>
        </div>
        <button className="btn btn-secondary" type="button" onClick={carregarRelatorio} disabled={carregando}>
          {carregando ? "Atualizando..." : "Recarregar"}
        </button>
      </div>

      {erro && (
        <div className="error-msg report-error" role="alert">
          <span>{erro}</span>
          <button className="btn btn-secondary" type="button" onClick={carregarRelatorio}>
            Tentar novamente
          </button>
        </div>
      )}

      {carregando ? (
        <div className="card report-loading" role="status">
          Carregando relatório...
        </div>
      ) : !erro && relatorio ? (
        <>
          <div className="report-summary" aria-label="Resumo de eventos">
            <article className="card report-metric">
              <p className="report-metric-label">Total de eventos</p>
              <p className="report-metric-value">{formatarNumero(relatorio.total_eventos)}</p>
            </article>
            <article className="card report-metric active-metric">
              <p className="report-metric-label">Eventos ativos</p>
              <p className="report-metric-value">{formatarNumero(relatorio.total_ativos)}</p>
            </article>
            <article className="card report-metric inactive-metric">
              <p className="report-metric-label">Eventos inativos</p>
              <p className="report-metric-value">{formatarNumero(relatorio.total_inativos)}</p>
            </article>
          </div>

          <div className="card report-table-card">
            <h3>Eventos por categoria</h3>
            <p>Quantidade total e situação dos eventos de cada categoria.</p>

            {categorias.length === 0 ? (
              <p className="report-empty">Ainda não existem categorias de eventos para exibir.</p>
            ) : (
              <div className="table-responsive">
                <table>
                  <thead>
                    <tr>
                      <th scope="col">Categoria</th>
                      <th scope="col">Total</th>
                      <th scope="col">Ativos</th>
                      <th scope="col">Inativos</th>
                    </tr>
                  </thead>
                  <tbody>
                    {categorias.map((categoria) => (
                      <tr key={categoria.categoria}>
                        <td>{categoria.categoria}</td>
                        <td>{formatarNumero(categoria.total)}</td>
                        <td>{formatarNumero(categoria.ativos)}</td>
                        <td>{formatarNumero(categoria.inativos)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      ) : null}
    </section>
  );
}

export default RelatorioEventos;
