from flask import Blueprint, jsonify, request

from app.services import evento_service
from app.utils.errors import ServiceError

evento_bp = Blueprint("eventos", __name__)


@evento_bp.get("")
def listar():
    eventos = evento_service.listar_eventos()
    return jsonify([e.to_dict() for e in eventos])


@evento_bp.get("/<int:evento_id>")
def buscar(evento_id):
    try:
        evento = evento_service.buscar_evento(evento_id)
        return jsonify(evento.to_dict())
    except ServiceError as erro:
        return jsonify({"erro": erro.message}), erro.status_code


@evento_bp.post("")
def criar():
    dados = request.get_json(silent=True) or {}
    try:
        evento = evento_service.criar_evento(dados)
        return jsonify(evento.to_dict()), 201
    except ServiceError as erro:
        return jsonify({"erro": erro.message}), erro.status_code


@evento_bp.put("/<int:evento_id>")
def atualizar(evento_id):
    dados = request.get_json(silent=True) or {}
    try:
        evento = evento_service.atualizar_evento(evento_id, dados)
        return jsonify(evento.to_dict())
    except ServiceError as erro:
        return jsonify({"erro": erro.message}), erro.status_code


@evento_bp.delete("/<int:evento_id>")
def remover(evento_id):
    try:
        evento_service.remover_evento(evento_id)
        return "", 204
    except ServiceError as erro:
        return jsonify({"erro": erro.message}), erro.status_code
