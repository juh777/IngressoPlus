from flask import Blueprint, jsonify

from app.controllers.base_controller import BaseController
from app.services.eventos import GerarRelatorioEventosService
from app.utils.errors import ServiceError

relatorio_evento_bp = Blueprint("relatorios_eventos", __name__)


class RelatorioEventoController(BaseController):
    """Controller HTTP de relatórios agregados do recurso Evento."""

    def __init__(self):
        self.gerar_relatorio_service = GerarRelatorioEventosService()

    def gerar(self):
        try:
            return jsonify(self.gerar_relatorio_service.executar())
        except ServiceError as erro:
            return self.responder_erro(erro)


relatorio_evento_controller = RelatorioEventoController()
relatorio_evento_bp.add_url_rule(
    "/eventos",
    "gerar_relatorio_eventos",
    relatorio_evento_controller.gerar,
    methods=["GET"],
)
