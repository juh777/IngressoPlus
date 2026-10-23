from app.utils.seguranca import exigir_admin
from flask import Blueprint, jsonify, request

from app.services import usuarios

usuario_bp = Blueprint('usuarios', __name__)

@usuario_bp.get('')
@exigir_admin
def listar():
    registros = usuarios.listar_usuarios()
    return jsonify([registro.to_dict() for registro in registros])

@usuario_bp.get('/<int:usuario_id>')
@exigir_admin
def buscar(usuario_id):
    registro = usuarios.buscar_usuario(usuario_id)
    return jsonify(registro.to_dict())

@usuario_bp.post('')
@exigir_admin
def criar():
    dados = request.get_json(silent=True)
    registro = usuarios.criar_usuario(dados)
    return jsonify(registro.to_dict()), 201

@usuario_bp.put('/<int:usuario_id>')
@exigir_admin
def atualizar(usuario_id):
    dados = request.get_json(silent=True)
    registro = usuarios.atualizar_usuario(usuario_id, dados)
    return jsonify(registro.to_dict())

@usuario_bp.delete('/<int:usuario_id>')
@exigir_admin
def remover(usuario_id):
    usuarios.remover_usuario(usuario_id)
    return '', 204

@usuario_bp.get('/busca')
@exigir_admin
def buscar_por_termo():
    registros = usuarios.buscar_usuarios_por_termo(request.args.get('termo'))
    return jsonify([registro.to_dict() for registro in registros])
