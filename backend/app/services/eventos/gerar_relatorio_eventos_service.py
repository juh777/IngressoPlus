from app.repositories.evento_repository import EventoRepository

def gerar_relatorio_eventos():
    linhas = EventoRepository.gerar_relatorio_por_categoria_status()
    categorias = {}
    total_eventos = 0
    total_ativos = 0
    total_inativos = 0

    for linha in linhas:
        nome = linha['categoria']
        if nome is None:
            nome = 'Sem categoria'
        if nome not in categorias:
            categorias[nome] = {'categoria': nome, 'total': 0, 'ativos': 0, 'inativos': 0}

        total = linha['total']
        categorias[nome]['total'] += total
        total_eventos += total
        if linha['ativo']:
            categorias[nome]['ativos'] += total
            total_ativos += total
        else:
            categorias[nome]['inativos'] += total
            total_inativos += total

    lista_categorias = list(categorias.values())
    lista_categorias.sort(key=lambda item: item['categoria'].casefold())
    return {
        'total_eventos': total_eventos,
        'total_ativos': total_ativos,
        'total_inativos': total_inativos,
        'categorias': lista_categorias,
    }
