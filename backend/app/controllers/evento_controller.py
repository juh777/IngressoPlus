from app.utils.seguranca import exigir_admin
from flask import Blueprint, jsonify, request

from app.services import eventos

evento_bp = Blueprint('eventos', __name__)

@evento_bp.get('')
def listar():
    registros = eventos.listar_eventos()
    return jsonify([registro.to_dict() for registro in registros])

@evento_bp.get('/<int:evento_id>')
def buscar(evento_id):
    registro = eventos.buscar_evento(evento_id)
    return jsonify(registro.to_dict())

@evento_bp.post('')
@exigir_admin
def criar():
    dados = request.get_json(silent=True)
    registro = eventos.criar_evento(dados)
    return jsonify(registro.to_dict()), 201

@evento_bp.put('/<int:evento_id>')
@exigir_admin
def atualizar(evento_id):
    dados = request.get_json(silent=True)
    registro = eventos.atualizar_evento(evento_id, dados)
    return jsonify(registro.to_dict())

@evento_bp.delete('/<int:evento_id>')
@exigir_admin
def remover(evento_id):
    eventos.remover_evento(evento_id)
    return '', 204

@evento_bp.get('/filtro')
def filtrar():
    registros = eventos.filtrar_eventos(
        categoria=request.args.get('categoria'),
        local=request.args.get('local'),
        status=request.args.get('status'),
    )
    return jsonify([registro.to_dict() for registro in registros])
