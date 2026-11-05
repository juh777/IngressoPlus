from app.extensions import transacao
from app.repositories import comunidade_repository as repository
from app.repositories.vendas_repository import buscar_lote
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
        lote = buscar_lote(lote_id)
        if not lote or lote['evento_id'] != evento_id:
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
        repository.bloquear_alertas_usuario(cursor, usuario_id)
        if repository.alerta_agendado(cursor, usuario_id, evento_id, lote_id):
            raise ServiceError('Já existe um alerta agendado para esta abertura.', 409)
        alerta_id = repository.inserir_alerta(cursor, usuario_id, evento_id, lote_id, tipo, data, agora())
    return {'id': alerta_id, 'agendado_em': data, 'canal': 'notificação dentro do sistema'}


def processar_alertas():
    repository.processar_alertas(agora())


def listar_alertas(usuario_id):
    processar_alertas()
    return repository.listar_alertas(usuario_id)


def alterar_alerta(usuario_id, alerta_id, dados):
    exigir_objeto(dados)
    alerta = repository.buscar_alerta(usuario_id, alerta_id)
    if not alerta:
        raise ServiceError('Alerta não encontrado.', 404)
    if dados.get('acao') == 'ler':
        repository.marcar_alerta_lido(usuario_id, alerta_id)
    elif dados.get('acao') == 'cancelar':
        repository.cancelar_alerta(usuario_id, alerta_id)
    else:
        raise ServiceError('Ação inválida.')
    return {'mensagem': 'Alerta atualizado.'}
