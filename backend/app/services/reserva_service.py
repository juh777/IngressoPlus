from datetime import timedelta
import secrets

from flask import current_app

from app.extensions import consultar, transacao
from app.repositories import vendas_repository as repository
from app.utils.errors import ServiceError
from app.utils.validators import exigir_objeto
from app.utils.vendas import agora, dinheiro, inteiro


def reservar_no_banco(cursor, usuario_id, dados):
    exigir_objeto(dados)
    lote_id = inteiro(dados.get('lote_id'), 'Lote')
    quantidade = inteiro(dados.get('quantidade', 1), 'Quantidade', 1, 10)
    tipo = dados.get('tipo', 'inteira')
    if tipo not in ['inteira', 'meia']:
        raise ServiceError('Escolha inteira ou meia-entrada.')
    cursor.execute('''SELECT l.*, e.ativo AS evento_ativo, e.data_hora_evento FROM lotes l
                      JOIN eventos e ON e.id = l.evento_id WHERE l.id = %s FOR UPDATE''', (lote_id,))
    lote = cursor.fetchone()
    if not lote:
        raise ServiceError('Lote não encontrado.', 404)
    if not lote['ativo'] or not lote['evento_ativo'] or not lote['inicio'] <= agora() <= lote['fim']:
        raise ServiceError('Este lote não está aberto para vendas.', 409)
    if lote['data_hora_evento'] <= agora():
        raise ServiceError('Este evento já aconteceu.', 409)
    if tipo == 'meia':
        cursor.execute('''SELECT id FROM documentos_meia WHERE usuario_id = %s
                          AND status = 'aprovado' AND validade >= %s LIMIT 1''',
                       (usuario_id, lote['data_hora_evento'].date()))
        if not cursor.fetchone():
            raise ServiceError('A meia-entrada exige um documento aprovado e válido na data do evento.', 409)
    cursor.execute('''SELECT COALESCE(SUM(quantidade), 0) AS total FROM reservas WHERE lote_id = %s
                      AND (status = 'paga' OR (status = 'reservada' AND expira_em > %s))''', (lote_id, agora()))
    if cursor.fetchone()['total'] + quantidade > lote['quantidade']:
        raise ServiceError('Quantidade indisponível. Atualize os lotes e tente novamente.', 409)

    assento_id = dados.get('assento_id')
    cursor.execute('SELECT COUNT(*) AS total FROM assentos WHERE evento_id = %s', (lote['evento_id'],))
    tem_mapa = cursor.fetchone()['total'] > 0
    if tem_mapa and not assento_id:
        raise ServiceError('Selecione um assento no mapa.')
    if assento_id:
        assento_id = inteiro(assento_id, 'Assento')
        if quantidade != 1:
            raise ServiceError('Reserve um ingresso por assento selecionado.')
        cursor.execute('SELECT id FROM assentos WHERE id = %s AND evento_id = %s FOR UPDATE',
                       (assento_id, lote['evento_id']))
        if not cursor.fetchone():
            raise ServiceError('O assento não pertence a este evento.')
        cursor.execute('''SELECT id FROM reservas WHERE assento_id = %s
                          AND (status = 'paga' OR (status = 'reservada' AND expira_em > %s)) LIMIT 1''',
                       (assento_id, agora()))
        if cursor.fetchone():
            raise ServiceError('Este assento acabou de ser ocupado. Escolha outro.', 409)
    preco = lote['preco'] if tipo == 'inteira' else dinheiro(lote['preco'] / 2)
    taxa = dinheiro(preco * quantidade * lote['taxa_percentual'] / 100)
    total = preco * quantidade + taxa
    cursor.execute('''INSERT INTO reservas (usuario_id, evento_id, lote_id, assento_id, quantidade, tipo,
                      preco_unitario, taxa_total, total, expira_em, criado_em)
                      VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                   (usuario_id, lote['evento_id'], lote_id, assento_id, quantidade, tipo,
                    preco, taxa, total, agora() + timedelta(minutes=15), agora()))
    return cursor.lastrowid


def criar_reserva(usuario_id, dados):
    with transacao() as cursor:
        reserva_id = reservar_no_banco(cursor, usuario_id, dados)
    return consultar('SELECT * FROM reservas WHERE id = %s', (reserva_id,), apenas_um=True)


def pagar_no_banco(cursor, usuario_id, reserva_id, resultado='aprovado'):
    if not current_app.config['MODO_DEMONSTRACAO']:
        raise ServiceError('O gateway externo não está habilitado nesta versão. Ative o modo demonstração.', 503)
    if resultado not in ['aprovado', 'recusado']:
        raise ServiceError('Resultado de simulação inválido.')
    cursor.execute('SELECT * FROM reservas WHERE id = %s FOR UPDATE', (reserva_id,))
    reserva = cursor.fetchone()
    if not reserva or reserva['usuario_id'] != usuario_id:
        raise ServiceError('Reserva não encontrada.', 404)
    if reserva['status'] == 'paga':
        return {'status': 'aprovado', 'reserva_id': reserva_id, 'modo': 'demonstracao', 'repetido': True}
    if reserva['status'] != 'reservada' or reserva['expira_em'] <= agora():
        raise ServiceError('A reserva expirou ou foi cancelada. Faça uma nova reserva.', 409)
    cursor.execute('SELECT ativo, data_hora_evento FROM eventos WHERE id = %s', (reserva['evento_id'],))
    evento = cursor.fetchone()
    if not evento['ativo'] or evento['data_hora_evento'] <= agora():
        raise ServiceError('Este evento não está disponível para pagamento.', 409)
    if reserva['tipo'] == 'meia':
        cursor.execute('''SELECT id FROM documentos_meia WHERE usuario_id = %s AND status = 'aprovado'
                          AND validade >= %s LIMIT 1''', (usuario_id, evento['data_hora_evento'].date()))
        if not cursor.fetchone():
            raise ServiceError('O documento de meia-entrada precisa estar aprovado.', 409)
    # A referência é estável por reserva. Repetir um pagamento aprovado não gera novos ingressos.
    referencia = 'demo-' + str(reserva_id)
    cursor.execute('''INSERT INTO pagamentos (reserva_id, valor, status, provedor, referencia, criado_em)
                      VALUES (%s,%s,%s,'simulador_local',%s,%s)
                      ON DUPLICATE KEY UPDATE status = VALUES(status)''',
                   (reserva_id, reserva['total'], resultado, referencia, agora()))
    if resultado == 'aprovado':
        cursor.execute("UPDATE reservas SET status = 'paga' WHERE id = %s", (reserva_id,))
        for _ in range(reserva['quantidade']):
            cursor.execute('''INSERT INTO ingressos (reserva_id, usuario_id, evento_id, assento_id, codigo, criado_em)
                              VALUES (%s,%s,%s,%s,%s,%s)''',
                           (reserva_id, usuario_id, reserva['evento_id'], reserva['assento_id'],
                            secrets.token_urlsafe(24), agora()))
    return {'status': resultado, 'reserva_id': reserva_id, 'modo': 'demonstracao',
            'mensagem': 'Simulação local: nenhum valor foi cobrado.'}


def pagar_reserva(usuario_id, reserva_id, dados):
    exigir_objeto(dados)
    with transacao() as cursor:
        return pagar_no_banco(cursor, usuario_id, reserva_id, dados.get('resultado', 'aprovado'))


def compra_expressa(usuario_id, dados):
    exigir_objeto(dados)
    if dados.get('confirmar_simulacao') is not True:
        raise ServiceError('Confirme que deseja simular a compra expressa.')
    with transacao() as cursor:
        reserva_id = reservar_no_banco(cursor, usuario_id, dados)
        return pagar_no_banco(cursor, usuario_id, reserva_id)


def cancelar_reserva(usuario_id, reserva_id):
    with transacao() as cursor:
        cursor.execute('''SELECT r.*, e.data_hora_evento FROM reservas r JOIN eventos e ON e.id = r.evento_id
                          WHERE r.id = %s FOR UPDATE''', (reserva_id,))
        reserva = cursor.fetchone()
        if not reserva or reserva['usuario_id'] != usuario_id:
            raise ServiceError('Reserva não encontrada.', 404)
        if reserva['status'] == 'cancelada':
            return {'status': 'cancelada'}
        if reserva['data_hora_evento'] <= agora():
            raise ServiceError('Não é possível cancelar após o início do evento.', 409)
        cursor.execute('SELECT id FROM ingressos WHERE reserva_id = %s AND utilizado_em IS NOT NULL', (reserva_id,))
        if cursor.fetchone():
            raise ServiceError('Ingresso já utilizado não pode ser cancelado.', 409)
        cursor.execute("UPDATE reservas SET status = 'cancelada' WHERE id = %s", (reserva_id,))
        cursor.execute("UPDATE pagamentos SET status = 'estornado' WHERE reserva_id = %s AND status = 'aprovado'", (reserva_id,))
    return {'status': 'cancelada', 'mensagem': 'Reserva liberada; eventual estorno é apenas uma simulação.'}


def validar_ingresso(codigo):
    if not isinstance(codigo, str) or not codigo or len(codigo) > 100:
        raise ServiceError('Código de ingresso inválido.')
    with transacao() as cursor:
        cursor.execute('''SELECT i.*, r.status, e.ativo, e.nome AS evento, u.nome AS titular
                          FROM ingressos i JOIN reservas r ON r.id = i.reserva_id
                          JOIN eventos e ON e.id = i.evento_id JOIN usuarios u ON u.id = i.usuario_id
                          WHERE i.codigo = %s FOR UPDATE''', (codigo,))
        ingresso = cursor.fetchone()
        if not ingresso:
            raise ServiceError('Ingresso não encontrado.', 404)
        if ingresso['status'] != 'paga' or not ingresso['ativo']:
            raise ServiceError('Ingresso cancelado ou evento indisponível.', 409)
        if ingresso['utilizado_em']:
            raise ServiceError('Este ingresso já foi utilizado.', 409)
        cursor.execute('UPDATE ingressos SET utilizado_em = %s WHERE id = %s', (agora(), ingresso['id']))
    return {'mensagem': 'Entrada confirmada.', 'evento': ingresso['evento'], 'titular': ingresso['titular']}


def expirar_reservas():
    from app.extensions import executar
    executar("UPDATE reservas SET status = 'expirada' WHERE status = 'reservada' AND expira_em <= %s", (agora(),))
