from app.repositories.evento_repository import EventoRepository


class GerarRelatorioEventosService:
    """Caso de uso: consolidar o relatório de eventos por categoria e status."""

    def executar(self) -> dict:
        linhas = EventoRepository.gerar_relatorio_por_categoria_status()
        categorias_por_nome: dict[str, dict] = {}
        total_eventos = 0
        total_ativos = 0
        total_inativos = 0

        for categoria, ativo, total in linhas:
            nome_categoria = categoria if categoria is not None else "Sem categoria"
            quantidade = int(total)
            resumo_categoria = categorias_por_nome.setdefault(
                nome_categoria,
                {
                    "categoria": nome_categoria,
                    "total": 0,
                    "ativos": 0,
                    "inativos": 0,
                },
            )

            resumo_categoria["total"] += quantidade
            total_eventos += quantidade
            if ativo:
                resumo_categoria["ativos"] += quantidade
                total_ativos += quantidade
            else:
                resumo_categoria["inativos"] += quantidade
                total_inativos += quantidade

        return {
            "total_eventos": total_eventos,
            "total_ativos": total_ativos,
            "total_inativos": total_inativos,
            "categorias": sorted(
                categorias_por_nome.values(),
                key=lambda resumo: resumo["categoria"].casefold(),
            ),
        }
