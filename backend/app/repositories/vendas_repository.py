from app.extensions import consultar, obter_conexao


def buscar_evento(evento_id):
    return consultar('SELECT * FROM eventos WHERE id = %s', (evento_id,), apenas_um=True)


def listar_lotes(evento_id):
    return consultar('''SELECT l.*, COALESCE(SUM(CASE WHEN r.status = 'paga'
                        OR (r.status = 'reservada' AND r.expira_em > UTC_TIMESTAMP(6))
                        THEN r.quantidade ELSE 0 END), 0) AS ocupados
                        FROM lotes l LEFT JOIN reservas r ON r.lote_id = l.id
                        WHERE l.evento_id = %s GROUP BY l.id ORDER BY l.inicio, l.id''', (evento_id,))


def mapa_assentos(evento_id):
    # A consulta de ocupação fica encapsulada na Stored Procedure do MySQL.
    with obter_conexao().cursor() as cursor:
        cursor.callproc('obter_mapa_assentos', (evento_id,))
        linhas = cursor.fetchall()
        while cursor.nextset():
            pass
        return linhas


def listar_reservas(usuario_id):
    return consultar('''SELECT r.*, e.nome AS evento, e.data_hora_evento, l.nome AS lote,
                        a.fila, a.numero, p.status AS pagamento_status
                        FROM reservas r JOIN eventos e ON e.id = r.evento_id
                        JOIN lotes l ON l.id = r.lote_id LEFT JOIN assentos a ON a.id = r.assento_id
                        LEFT JOIN pagamentos p ON p.reserva_id = r.id
                        WHERE r.usuario_id = %s ORDER BY r.id DESC''', (usuario_id,))


def listar_ingressos(usuario_id):
    return consultar('''SELECT i.id, i.codigo, i.utilizado_em, i.criado_em, r.status, e.nome AS evento,
                        e.data_hora_evento, e.`local`, r.tipo, r.preco_unitario, a.setor, a.fila, a.numero
                        FROM ingressos i JOIN eventos e ON e.id = i.evento_id
                        JOIN reservas r ON r.id = i.reserva_id LEFT JOIN assentos a ON a.id = i.assento_id
                        WHERE i.usuario_id = %s ORDER BY e.data_hora_evento, i.id''', (usuario_id,))


def relatorio_vendas(evento_id):
    # Pagamentos, reservas e ingressos são agregados separadamente: sem multiplicar totais nos JOINs.
    totais = consultar('''SELECT COUNT(*) AS compras, COALESCE(SUM(quantidade), 0) AS ingressos,
                         COALESCE(SUM(total), 0) AS arrecadacao, COALESCE(SUM(taxa_total), 0) AS taxas
                         FROM reservas WHERE evento_id = %s AND status = 'paga' ''', (evento_id,), apenas_um=True)
    totais['por_lote'] = consultar('''SELECT l.id, l.nome, l.quantidade,
                         COALESCE(SUM(CASE WHEN r.status = 'paga' THEN r.quantidade ELSE 0 END), 0) AS vendidos,
                         COALESCE(SUM(CASE WHEN r.status = 'paga' THEN r.total ELSE 0 END), 0) AS receita
                         FROM lotes l LEFT JOIN reservas r ON r.lote_id = l.id WHERE l.evento_id = %s
                         GROUP BY l.id ORDER BY l.id''', (evento_id,))
    totais['reservas_por_status'] = consultar('''SELECT status, COUNT(*) AS total FROM reservas
                                              WHERE evento_id = %s GROUP BY status''', (evento_id,))
    totais['ingressos'] = int(totais['ingressos'])
    for lote in totais['por_lote']:
        lote['vendidos'] = int(lote['vendidos'])
    return totais
