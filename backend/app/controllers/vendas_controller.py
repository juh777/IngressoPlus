from flask import Blueprint, jsonify, request

from app.repositories import vendas_repository as repository
from app.services import lote_service, reserva_service
from app.utils.seguranca import exigir_admin, exigir_login, usuario_atual
from app.utils.validators import exigir_objeto
from app.utils.vendas import serializar

vendas_bp = Blueprint('vendas', __name__)


def resposta(dados, status=200):
    return jsonify(serializar(dados)), status


@vendas_bp.get('/eventos/<int:evento_id>/lotes')
def lotes(evento_id):
    return resposta(lote_service.consultar_lotes(evento_id))


@vendas_bp.post('/eventos/<int:evento_id>/lotes')
@exigir_admin
def criar_lote(evento_id):
    return resposta(lote_service.cadastrar_lote(evento_id, request.get_json(silent=True)), 201)


@vendas_bp.get('/eventos/<int:evento_id>/assentos')
def assentos(evento_id):
    lote_service.evento_existente(evento_id)
    return resposta(repository.mapa_assentos(evento_id))


@vendas_bp.post('/eventos/<int:evento_id>/assentos')
@exigir_admin
def criar_assentos(evento_id):
    return resposta(lote_service.gerar_assentos(evento_id, request.get_json(silent=True)), 201)


@vendas_bp.get('/lotes/<int:lote_id>/taxas')
def taxas(lote_id):
    return resposta(lote_service.comparar_taxas(lote_id, request.args.get('quantidade', 1), request.args.get('tipo', 'inteira')))


@vendas_bp.post('/reservas')
@exigir_login
def reservar():
    return resposta(reserva_service.criar_reserva(usuario_atual()['id'], request.get_json(silent=True)), 201)


@vendas_bp.get('/reservas')
@exigir_login
def minhas_reservas():
    reserva_service.expirar_reservas()
    return resposta(repository.listar_reservas(usuario_atual()['id']))


@vendas_bp.post('/reservas/<int:reserva_id>/pagamento')
@exigir_login
def pagar(reserva_id):
    return resposta(reserva_service.pagar_reserva(usuario_atual()['id'], reserva_id, request.get_json(silent=True)))


@vendas_bp.post('/reservas/<int:reserva_id>/cancelar')
@exigir_login
def cancelar(reserva_id):
    return resposta(reserva_service.cancelar_reserva(usuario_atual()['id'], reserva_id))


@vendas_bp.post('/checkout/expressa')
@exigir_login
def expressa():
    return resposta(reserva_service.compra_expressa(usuario_atual()['id'], request.get_json(silent=True)), 201)


@vendas_bp.get('/ingressos')
@exigir_login
def ingressos():
    return resposta(repository.listar_ingressos(usuario_atual()['id']))


@vendas_bp.post('/ingressos/validar')
@exigir_admin
def validar():
    dados = exigir_objeto(request.get_json(silent=True))
    return resposta(reserva_service.validar_ingresso(dados.get('codigo')))


@vendas_bp.get('/relatorios/vendas/<int:evento_id>')
@exigir_admin
def vendas(evento_id):
    lote_service.evento_existente(evento_id)
    reserva_service.expirar_reservas()
    return resposta(repository.relatorio_vendas(evento_id))
