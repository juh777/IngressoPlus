from flask import Blueprint, jsonify, request

from app.services import usuario_service
from app.utils.errors import ServiceError

usuario_bp = Blueprint("usuarios", __name__)


@usuario_bp.get("")
def listar():
    usuarios = usuario_service.listar_usuarios()
    return jsonify([u.to_dict() for u in usuarios])


@usuario_bp.get("/<int:usuario_id>")
def buscar(usuario_id):
    try:
        usuario = usuario_service.buscar_usuario(usuario_id)
        return jsonify(usuario.to_dict())
    except ServiceError as erro:
        return jsonify({"erro": erro.message}), erro.status_code


@usuario_bp.post("")
def criar():
    dados = request.get_json(silent=True) or {}
    try:
        usuario = usuario_service.criar_usuario(dados)
        return jsonify(usuario.to_dict()), 201
    except ServiceError as erro:
        return jsonify({"erro": erro.message}), erro.status_code


@usuario_bp.put("/<int:usuario_id>")
def atualizar(usuario_id):
    dados = request.get_json(silent=True) or {}
    try:
        usuario = usuario_service.atualizar_usuario(usuario_id, dados)
        return jsonify(usuario.to_dict())
    except ServiceError as erro:
        return jsonify({"erro": erro.message}), erro.status_code


@usuario_bp.delete("/<int:usuario_id>")
def remover(usuario_id):
    try:
        usuario_service.remover_usuario(usuario_id)
        return "", 204
    except ServiceError as erro:
        return jsonify({"erro": erro.message}), erro.status_code
