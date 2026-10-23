from flask import Blueprint, jsonify, request, session

from app.services import conta_service as conta
from app.utils.seguranca import exigir_login, usuario_atual
from app.utils.vendas import serializar

conta_bp = Blueprint('conta', __name__)


@conta_bp.post('/auth/login')
def login():
    return jsonify(conta.entrar(request.get_json(silent=True)))


@conta_bp.post('/auth/cadastro')
def cadastro():
    return jsonify(conta.cadastrar(request.get_json(silent=True))), 201


@conta_bp.post('/auth/logout')
def logout():
    session.clear()
    return '', 204


@conta_bp.get('/auth/sessao')
@exigir_login
def sessao():
    return jsonify(usuario_atual())


@conta_bp.put('/perfil')
@exigir_login
def perfil():
    return jsonify(conta.atualizar_perfil(usuario_atual()['id'], request.get_json(silent=True)))


@conta_bp.get('/perfil/cofre')
@exigir_login
def cofre():
    return jsonify(conta.ler_cofre(usuario_atual()['id']))


@conta_bp.put('/perfil/cofre')
@exigir_login
def salvar_cofre():
    return jsonify(conta.salvar_cofre(usuario_atual()['id'], request.get_json(silent=True)))


@conta_bp.get('/perfil/exportar')
@exigir_login
def exportar():
    resposta = jsonify(serializar(conta.exportar_dados(usuario_atual()['id'])))
    resposta.headers['Content-Disposition'] = 'attachment; filename=meus-dados-ingressoplus.json'
    resposta.headers['Cache-Control'] = 'no-store'
    return resposta
