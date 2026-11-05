"""Consultas e gravações de documentos, grupos e alertas."""
from app.extensions import consultar, executar


def inserir_documento(usuario_id, tipo, nome, mime, conteudo, validade, agora):
    return executar('''INSERT INTO documentos_meia
                       (usuario_id, tipo, nome_arquivo, mime, conteudo, validade, criado_em)
                       VALUES (%s,%s,%s,%s,%s,%s,%s)''', (usuario_id, tipo, nome, mime, conteudo, validade, agora))


def buscar_documento(documento_id):
    return consultar('SELECT * FROM documentos_meia WHERE id = %s', (documento_id,), apenas_um=True)


def listar_documentos(usuario_id=None):
    sql = '''SELECT d.id, d.usuario_id, d.tipo, d.nome_arquivo, d.validade, d.status,
             d.observacao, d.criado_em, u.nome AS titular FROM documentos_meia d
             JOIN usuarios u ON u.id = d.usuario_id'''
    if usuario_id is None:
        return consultar(sql + ' ORDER BY d.id DESC')
    return consultar(sql + ' WHERE d.usuario_id = %s ORDER BY d.id DESC', (usuario_id,))


def atualizar_documento(documento_id, status, observacao):
    executar('UPDATE documentos_meia SET status = %s, observacao = %s WHERE id = %s', (status, observacao, documento_id))


def listar_grupos(usuario_id):
    return consultar('''SELECT g.*, e.nome AS evento FROM grupos g JOIN eventos e ON e.id = g.evento_id
                        JOIN grupo_membros m ON m.grupo_id = g.id WHERE m.usuario_id = %s ORDER BY g.id DESC''', (usuario_id,))


def inserir_grupo(cursor, evento_id, usuario_id, nome, codigo, agora):
    cursor.execute('INSERT INTO grupos (evento_id, criador_id, nome, codigo, criado_em) VALUES (%s,%s,%s,%s,%s)',
                   (evento_id, usuario_id, nome, codigo, agora))
    grupo_id = cursor.lastrowid
    inserir_membro(cursor, grupo_id, usuario_id)
    return grupo_id


def bloquear_grupo_por_codigo(cursor, codigo):
    cursor.execute('SELECT * FROM grupos WHERE codigo = %s FOR UPDATE', (codigo,))
    return cursor.fetchone()


def bloquear_grupo(cursor, grupo_id):
    cursor.execute('SELECT * FROM grupos WHERE id = %s FOR UPDATE', (grupo_id,))
    return cursor.fetchone()


def listar_membros(cursor, grupo_id):
    cursor.execute('SELECT usuario_id FROM grupo_membros WHERE grupo_id = %s', (grupo_id,))
    return cursor.fetchall()


def inserir_membro(cursor, grupo_id, usuario_id):
    cursor.execute('INSERT INTO grupo_membros (grupo_id, usuario_id) VALUES (%s,%s)', (grupo_id, usuario_id))


def buscar_grupo_do_membro(usuario_id, grupo_id):
    return consultar('''SELECT g.*, e.nome AS evento FROM grupos g JOIN eventos e ON e.id = g.evento_id
                        JOIN grupo_membros m ON m.grupo_id = g.id
                        WHERE g.id = %s AND m.usuario_id = %s''', (grupo_id, usuario_id), apenas_um=True)


def resumo_membros(evento_id, grupo_id):
    return consultar('''SELECT u.id, u.nome,
        COALESCE(SUM(CASE WHEN r.status = 'paga' THEN r.total ELSE 0 END), 0) AS total_pago,
        COALESCE(SUM(CASE WHEN r.status = 'paga' THEN r.quantidade ELSE 0 END), 0) AS ingressos
        FROM grupo_membros m JOIN usuarios u ON u.id = m.usuario_id
        LEFT JOIN reservas r ON r.usuario_id = u.id AND r.evento_id = %s
        WHERE m.grupo_id = %s GROUP BY u.id ORDER BY u.nome''', (evento_id, grupo_id))


def remover_membro(cursor, grupo_id, usuario_id):
    cursor.execute('DELETE FROM grupo_membros WHERE grupo_id = %s AND usuario_id = %s', (grupo_id, usuario_id))


def bloquear_alertas_usuario(cursor, usuario_id):
    cursor.execute('SELECT id FROM usuarios WHERE id = %s FOR UPDATE', (usuario_id,))


def alerta_agendado(cursor, usuario_id, evento_id, lote_id):
    cursor.execute('''SELECT id FROM alertas WHERE usuario_id = %s AND evento_id = %s
                      AND lote_id <=> %s AND status = 'agendado' ''', (usuario_id, evento_id, lote_id))
    return bool(cursor.fetchone())


def inserir_alerta(cursor, usuario_id, evento_id, lote_id, tipo, data, agora):
    cursor.execute('''INSERT INTO alertas (usuario_id, evento_id, lote_id, tipo, agendado_em, criado_em)
                      VALUES (%s,%s,%s,%s,%s,%s)''', (usuario_id, evento_id, lote_id, tipo, data, agora))
    return cursor.lastrowid


def processar_alertas(agora):
    executar("""UPDATE alertas a JOIN eventos e ON e.id = a.evento_id
                 SET a.status = 'enviado' WHERE a.status = 'agendado'
                 AND a.agendado_em <= %s AND e.ativo = TRUE AND e.data_hora_evento > %s""", (agora, agora))
    executar("""UPDATE alertas a JOIN eventos e ON e.id = a.evento_id SET a.status = 'cancelado'
                 WHERE a.status = 'agendado' AND (e.ativo = FALSE OR e.data_hora_evento <= %s)""", (agora,))


def listar_alertas(usuario_id):
    return consultar('''SELECT a.*, e.nome AS evento, l.nome AS lote FROM alertas a
                        JOIN eventos e ON e.id = a.evento_id LEFT JOIN lotes l ON l.id = a.lote_id
                        WHERE a.usuario_id = %s ORDER BY a.id DESC''', (usuario_id,))


def buscar_alerta(usuario_id, alerta_id):
    return consultar('SELECT * FROM alertas WHERE id = %s AND usuario_id = %s', (alerta_id, usuario_id), apenas_um=True)


def marcar_alerta_lido(usuario_id, alerta_id):
    executar('UPDATE alertas SET lido = TRUE WHERE id = %s AND usuario_id = %s', (alerta_id, usuario_id))


def cancelar_alerta(usuario_id, alerta_id):
    executar("UPDATE alertas SET status = 'cancelado' WHERE id = %s AND usuario_id = %s", (alerta_id, usuario_id))
