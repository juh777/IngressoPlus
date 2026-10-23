from app.extensions import consultar, executar, transacao
from app.services.lote_service import evento_existente
from app.services.eventos.helpers import data_hora_iso
from app.utils.errors import ServiceError
from app.utils.validators import exigir_objeto
from app.utils.vendas import agora, inteiro


def agendar_alerta(usuario_id, dados):
    exigir_objeto(dados)
    evento_id = inteiro(dados.get('evento_id'), 'Evento')
    evento = evento_existente(evento_id)
    lote_id = dados.get('lote_id')
    tipo = 'lote' if lote_id else 'abertura'
    data = evento['data_abertura_vendas']
    if lote_id:
        lote_id = inteiro(lote_id, 'Lote')
        lote = consultar('SELECT inicio FROM lotes WHERE id = %s AND evento_id = %s', (lote_id, evento_id), apenas_um=True)
        if not lote:
            raise ServiceError('O lote não pertence a este evento.')
        data = lote['inicio']
    if dados.get('agendado_em'):
        data = data_hora_iso(dados['agendado_em'], 'agendado_em')
    if data >= evento['data_hora_evento'] or evento['data_hora_evento'] <= agora() or not evento['ativo']:
        raise ServiceError('O alerta deve acontecer antes de um evento ativo e futuro.')
    if data < agora():
        data = agora()
    with transacao() as cursor:
        # Serializa os agendamentos do mesmo usuário para evitar duplicidade.
        cursor.execute('SELECT id FROM usuarios WHERE id = %s FOR UPDATE', (usuario_id,))
        cursor.execute('''SELECT id FROM alertas WHERE usuario_id = %s AND evento_id = %s
                          AND lote_id <=> %s AND status = 'agendado' ''', (usuario_id, evento_id, lote_id))
        if cursor.fetchone():
            raise ServiceError('Já existe um alerta agendado para esta abertura.', 409)
        cursor.execute('''INSERT INTO alertas (usuario_id, evento_id, lote_id, tipo, agendado_em, criado_em)
                          VALUES (%s,%s,%s,%s,%s,%s)''', (usuario_id, evento_id, lote_id, tipo, data, agora()))
        alerta_id = cursor.lastrowid
    return {'id': alerta_id, 'agendado_em': data, 'canal': 'notificação dentro do sistema'}


def processar_alertas():
    executar("""UPDATE alertas a JOIN eventos e ON e.id = a.evento_id
                 SET a.status = 'enviado' WHERE a.status = 'agendado'
                 AND a.agendado_em <= %s AND e.ativo = TRUE AND e.data_hora_evento > %s""", (agora(), agora()))
    executar("""UPDATE alertas a JOIN eventos e ON e.id = a.evento_id SET a.status = 'cancelado'
                 WHERE a.status = 'agendado' AND (e.ativo = FALSE OR e.data_hora_evento <= %s)""", (agora(),))


def listar_alertas(usuario_id):
    processar_alertas()
    return consultar('''SELECT a.*, e.nome AS evento, l.nome AS lote FROM alertas a
                        JOIN eventos e ON e.id = a.evento_id LEFT JOIN lotes l ON l.id = a.lote_id
                        WHERE a.usuario_id = %s ORDER BY a.id DESC''', (usuario_id,))


def alterar_alerta(usuario_id, alerta_id, dados):
    exigir_objeto(dados)
    alerta = consultar('SELECT * FROM alertas WHERE id = %s AND usuario_id = %s', (alerta_id, usuario_id), apenas_um=True)
    if not alerta:
        raise ServiceError('Alerta não encontrado.', 404)
    if dados.get('acao') == 'ler':
        executar('UPDATE alertas SET lido = TRUE WHERE id = %s AND usuario_id = %s', (alerta_id, usuario_id))
    elif dados.get('acao') == 'cancelar':
        executar("UPDATE alertas SET status = 'cancelado' WHERE id = %s AND usuario_id = %s", (alerta_id, usuario_id))
    else:
        raise ServiceError('Ação inválida.')
    return {'mensagem': 'Alerta atualizado.'}
