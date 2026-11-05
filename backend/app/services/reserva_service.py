from datetime import timedelta
import secrets

from flask import current_app

from app.extensions import transacao
from app.repositories import vendas_repository as repository
from app.services.lote_service import evento_existente
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
    lote = repository.bloquear_lote(cursor, lote_id)
    if not lote:
        raise ServiceError('Lote não encontrado.', 404)
    if not lote['ativo'] or not lote['evento_ativo'] or not lote['inicio'] <= agora() <= lote['fim']:
        raise ServiceError('Este lote não está aberto para vendas.', 409)
    if lote['data_hora_evento'] <= agora():
        raise ServiceError('Este evento já aconteceu.', 409)
    if tipo == 'meia' and not repository.documento_valido(cursor, usuario_id, lote['data_hora_evento'].date()):
        raise ServiceError('A meia-entrada exige um documento aprovado e válido na data do evento.', 409)
    if repository.quantidade_ocupada(cursor, lote_id, agora()) + quantidade > lote['quantidade']:
        raise ServiceError('Quantidade indisponível. Atualize os lotes e tente novamente.', 409)

    assento_id = dados.get('assento_id')
    tem_mapa = repository.evento_tem_assentos(cursor, lote['evento_id'])
    if tem_mapa and not assento_id:
        raise ServiceError('Selecione um assento no mapa.')
    if assento_id:
        assento_id = inteiro(assento_id, 'Assento')
        if quantidade != 1:
            raise ServiceError('Reserve um ingresso por assento selecionado.')
        if not repository.bloquear_assento(cursor, assento_id, lote['evento_id']):
            raise ServiceError('O assento não pertence a este evento.')
        if repository.assento_ocupado(cursor, assento_id, agora()):
            raise ServiceError('Este assento acabou de ser ocupado. Escolha outro.', 409)
    preco = lote['preco'] if tipo == 'inteira' else dinheiro(lote['preco'] / 2)
    taxa = dinheiro(preco * quantidade * lote['taxa_percentual'] / 100)
    total = preco * quantidade + taxa
    return repository.inserir_reserva(cursor, (
        usuario_id, lote['evento_id'], lote_id, assento_id, quantidade, tipo,
        preco, taxa, total, agora() + timedelta(minutes=15), agora()))


def criar_reserva(usuario_id, dados):
    with transacao() as cursor:
        reserva_id = reservar_no_banco(cursor, usuario_id, dados)
    return repository.buscar_reserva(reserva_id)


def pagar_no_banco(cursor, usuario_id, reserva_id, resultado='aprovado'):
    if not current_app.config['MODO_DEMONSTRACAO']:
        raise ServiceError('O gateway externo não está habilitado nesta versão. Ative o modo demonstração.', 503)
    if resultado not in ['aprovado', 'recusado']:
        raise ServiceError('Resultado de simulação inválido.')
    reserva = repository.bloquear_reserva(cursor, reserva_id)
    if not reserva or reserva['usuario_id'] != usuario_id:
        raise ServiceError('Reserva não encontrada.', 404)
    if reserva['status'] == 'paga':
        return {'status': 'aprovado', 'reserva_id': reserva_id, 'modo': 'demonstracao', 'repetido': True}
    if reserva['status'] != 'reservada' or reserva['expira_em'] <= agora():
        raise ServiceError('A reserva expirou ou foi cancelada. Faça uma nova reserva.', 409)
    evento = repository.buscar_evento_reserva(cursor, reserva['evento_id'])
    if not evento['ativo'] or evento['data_hora_evento'] <= agora():
        raise ServiceError('Este evento não está disponível para pagamento.', 409)
    if reserva['tipo'] == 'meia' and not repository.documento_valido(cursor, usuario_id, evento['data_hora_evento'].date()):
        raise ServiceError('O documento de meia-entrada precisa estar aprovado.', 409)
    # A referência é estável por reserva. Repetir um pagamento aprovado não gera novos ingressos.
    referencia = 'demo-' + str(reserva_id)
    repository.registrar_pagamento(cursor, reserva_id, reserva['total'], resultado, referencia, agora())
    if resultado == 'aprovado':
        repository.confirmar_reserva(cursor, reserva_id)
        for _ in range(reserva['quantidade']):
            repository.inserir_ingresso(cursor, reserva, secrets.token_urlsafe(24), agora())
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
        reserva = repository.bloquear_reserva_com_evento(cursor, reserva_id)
        if not reserva or reserva['usuario_id'] != usuario_id:
            raise ServiceError('Reserva não encontrada.', 404)
        if reserva['status'] == 'cancelada':
            return {'status': 'cancelada'}
        if reserva['data_hora_evento'] <= agora():
            raise ServiceError('Não é possível cancelar após o início do evento.', 409)
        if repository.reserva_utilizada(cursor, reserva_id):
            raise ServiceError('Ingresso já utilizado não pode ser cancelado.', 409)
        repository.cancelar_reserva(cursor, reserva_id)
    return {'status': 'cancelada', 'mensagem': 'Reserva liberada; eventual estorno é apenas uma simulação.'}


def validar_ingresso(codigo):
    if not isinstance(codigo, str) or not codigo or len(codigo) > 100:
        raise ServiceError('Código de ingresso inválido.')
    with transacao() as cursor:
        ingresso = repository.bloquear_ingresso(cursor, codigo)
        if not ingresso:
            raise ServiceError('Ingresso não encontrado.', 404)
        if ingresso['status'] != 'paga' or not ingresso['ativo']:
            raise ServiceError('Ingresso cancelado ou evento indisponível.', 409)
        if ingresso['utilizado_em']:
            raise ServiceError('Este ingresso já foi utilizado.', 409)
        repository.marcar_ingresso_utilizado(cursor, ingresso['id'], agora())
    return {'mensagem': 'Entrada confirmada.', 'evento': ingresso['evento'], 'titular': ingresso['titular']}


def expirar_reservas():
    repository.expirar_reservas(agora())


def listar_reservas(usuario_id):
    expirar_reservas()
    return repository.listar_reservas(usuario_id)


def listar_ingressos(usuario_id):
    return repository.listar_ingressos(usuario_id)


def relatorio_vendas(evento_id):
    evento_existente(evento_id)
    expirar_reservas()
    return repository.relatorio_vendas(evento_id)
