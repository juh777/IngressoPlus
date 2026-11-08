from app.extensions import consultar, executar, obter_conexao


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


def buscar_lote(lote_id):
    return consultar('SELECT * FROM lotes WHERE id = %s', (lote_id,), apenas_um=True)


def inserir_lote(dados):
    return executar('''INSERT INTO lotes (evento_id, nome, preco, quantidade, taxa_percentual, inicio, fim)
                       VALUES (%s, %s, %s, %s, %s, %s, %s)''', dados)


def bloquear_evento(cursor, evento_id):
    cursor.execute('SELECT id FROM eventos WHERE id = %s FOR UPDATE', (evento_id,))


def evento_tem_reservas(cursor, evento_id):
    cursor.execute('SELECT id FROM reservas WHERE evento_id = %s LIMIT 1', (evento_id,))
    return bool(cursor.fetchone())


def evento_tem_assentos(cursor, evento_id):
    cursor.execute('SELECT id FROM assentos WHERE evento_id = %s LIMIT 1', (evento_id,))
    return bool(cursor.fetchone())


def inserir_assento(cursor, evento_id, setor, fila, numero):
    cursor.execute('INSERT INTO assentos (evento_id, setor, fila, numero) VALUES (%s, %s, %s, %s)',
                   (evento_id, setor, fila, numero))


def bloquear_lote(cursor, lote_id):
    cursor.execute('''SELECT l.*, e.ativo AS evento_ativo, e.data_hora_evento FROM lotes l
                      JOIN eventos e ON e.id = l.evento_id WHERE l.id = %s FOR UPDATE''', (lote_id,))
    return cursor.fetchone()


def documento_valido(cursor, usuario_id, data_evento):
    cursor.execute('''SELECT id FROM documentos_meia WHERE usuario_id = %s
                      AND status = 'aprovado' AND validade >= %s LIMIT 1''', (usuario_id, data_evento))
    return bool(cursor.fetchone())


def quantidade_ocupada(cursor, lote_id, agora):
    cursor.execute('''SELECT COALESCE(SUM(quantidade), 0) AS total FROM reservas WHERE lote_id = %s
                      AND (status = 'paga' OR (status = 'reservada' AND expira_em > %s))''', (lote_id, agora))
    return cursor.fetchone()['total']


def bloquear_assento(cursor, assento_id, evento_id):
    cursor.execute('SELECT id FROM assentos WHERE id = %s AND evento_id = %s FOR UPDATE', (assento_id, evento_id))
    return cursor.fetchone()


def assento_ocupado(cursor, assento_id, agora):
    cursor.execute('''SELECT id FROM reservas WHERE assento_id = %s
                      AND (status = 'paga' OR (status = 'reservada' AND expira_em > %s)) LIMIT 1''', (assento_id, agora))
    return bool(cursor.fetchone())


def inserir_reserva(cursor, dados):
    cursor.execute('''INSERT INTO reservas (usuario_id, evento_id, lote_id, assento_id, quantidade, tipo,
                      preco_unitario, taxa_total, total, expira_em, criado_em)
                      VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', dados)
    return cursor.lastrowid


def buscar_reserva(reserva_id):
    return consultar('SELECT * FROM reservas WHERE id = %s', (reserva_id,), apenas_um=True)


def bloquear_reserva(cursor, reserva_id):
    cursor.execute('SELECT * FROM reservas WHERE id = %s FOR UPDATE', (reserva_id,))
    return cursor.fetchone()


def buscar_evento_reserva(cursor, evento_id):
    cursor.execute('SELECT ativo, data_hora_evento FROM eventos WHERE id = %s', (evento_id,))
    return cursor.fetchone()


def registrar_pagamento(cursor, reserva_id, valor, resultado, referencia, agora):
    cursor.execute('''INSERT INTO pagamentos (reserva_id, valor, status, provedor, referencia, criado_em)
                      VALUES (%s,%s,%s,'simulador_local',%s,%s)
                      ON DUPLICATE KEY UPDATE status = VALUES(status)''',
                   (reserva_id, valor, resultado, referencia, agora))


def confirmar_reserva(cursor, reserva_id):
    cursor.execute("UPDATE reservas SET status = 'paga' WHERE id = %s", (reserva_id,))


def inserir_ingresso(cursor, reserva, codigo, agora):
    cursor.execute('''INSERT INTO ingressos (reserva_id, usuario_id, evento_id, assento_id, codigo, criado_em)
                      VALUES (%s,%s,%s,%s,%s,%s)''',
                   (reserva['id'], reserva['usuario_id'], reserva['evento_id'], reserva['assento_id'], codigo, agora))


def bloquear_reserva_com_evento(cursor, reserva_id):
    cursor.execute('''SELECT r.*, e.data_hora_evento FROM reservas r JOIN eventos e ON e.id = r.evento_id
                      WHERE r.id = %s FOR UPDATE''', (reserva_id,))
    return cursor.fetchone()


def reserva_utilizada(cursor, reserva_id):
    cursor.execute('SELECT id FROM ingressos WHERE reserva_id = %s AND utilizado_em IS NOT NULL', (reserva_id,))
    return bool(cursor.fetchone())


def cancelar_reserva(cursor, reserva_id):
    cursor.execute("UPDATE reservas SET status = 'cancelada' WHERE id = %s", (reserva_id,))
    cursor.execute("UPDATE pagamentos SET status = 'estornado' WHERE reserva_id = %s AND status = 'aprovado'", (reserva_id,))


def bloquear_ingresso(cursor, codigo):
    cursor.execute('''SELECT i.*, r.status, e.ativo, e.nome AS evento, u.nome AS titular
                      FROM ingressos i JOIN reservas r ON r.id = i.reserva_id
                      JOIN eventos e ON e.id = i.evento_id JOIN usuarios u ON u.id = i.usuario_id
                      WHERE i.codigo = %s FOR UPDATE''', (codigo,))
    return cursor.fetchone()


def marcar_ingresso_utilizado(cursor, ingresso_id, agora):
    cursor.execute('UPDATE ingressos SET utilizado_em = %s WHERE id = %s', (agora, ingresso_id))


def expirar_reservas(agora):
    executar("UPDATE reservas SET status = 'expirada' WHERE status = 'reservada' AND expira_em <= %s", (agora,))


def historico_categorias(usuario_id):
    return consultar('''SELECT e.categoria, COUNT(*) AS total FROM reservas r JOIN eventos e ON e.id = r.evento_id
                        WHERE r.usuario_id = %s AND r.status = 'paga' GROUP BY e.categoria''', (usuario_id,))
