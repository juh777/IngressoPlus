from app.utils.seguranca import exigir_admin
from flask import Blueprint, jsonify
from app.services.eventos import gerar_relatorio_eventos

relatorio_evento_bp = Blueprint('relatorios_eventos', __name__)

@relatorio_evento_bp.get('/eventos')
@exigir_admin
def gerar():
    return jsonify(gerar_relatorio_eventos())
