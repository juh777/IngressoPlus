from flask import Blueprint, jsonify, request

from app.controllers.base_controller import BaseController
from app.services.eventos import (
    AtualizarEventoService,
    BuscarEventoService,
    CriarEventoService,
    ExcluirEventoService,
    FiltrarEventosService,
    ListarEventosService,
)
from app.utils.errors import ServiceError

evento_bp = Blueprint("eventos", __name__)


class EventoController(BaseController):
    """Controller HTTP do recurso Evento; regras ficam nos services."""

    def __init__(self):
        self.listar_service = ListarEventosService()
        self.buscar_service = BuscarEventoService()
        self.filtrar_service = FiltrarEventosService()
        self.criar_service = CriarEventoService()
        self.atualizar_service = AtualizarEventoService()
        self.excluir_service = ExcluirEventoService()

    def listar(self):
        try:
            eventos = self.listar_service.executar()
            return jsonify([evento.to_dict() for evento in eventos])
        except ServiceError as erro:
            return self.responder_erro(erro)

    def buscar(self, evento_id: int):
        try:
            evento = self.buscar_service.executar(evento_id)
            return jsonify(evento.to_dict())
        except ServiceError as erro:
            return self.responder_erro(erro)

    def filtrar(self):
        try:
            eventos = self.filtrar_service.executar(
                categoria=request.args.get("categoria"),
                local=request.args.get("local"),
                status=request.args.get("status"),
            )
            return jsonify([evento.to_dict() for evento in eventos])
        except ServiceError as erro:
            return self.responder_erro(erro)

    def criar(self):
        dados = request.get_json(silent=True) or {}
        try:
            evento = self.criar_service.executar(dados)
            return jsonify(evento.to_dict()), 201
        except ServiceError as erro:
            return self.responder_erro(erro)

    def atualizar(self, evento_id: int):
        dados = request.get_json(silent=True) or {}
        try:
            evento = self.atualizar_service.executar(evento_id, dados)
            return jsonify(evento.to_dict())
        except ServiceError as erro:
            return self.responder_erro(erro)

    def remover(self, evento_id: int):
        try:
            self.excluir_service.executar(evento_id)
            return "", 204
        except ServiceError as erro:
            return self.responder_erro(erro)


evento_controller = EventoController()
evento_bp.add_url_rule("", "listar_eventos", evento_controller.listar, methods=["GET"])
evento_bp.add_url_rule("/filtro", "filtrar_eventos", evento_controller.filtrar, methods=["GET"])
evento_bp.add_url_rule("/<int:evento_id>", "buscar_evento", evento_controller.buscar, methods=["GET"])
evento_bp.add_url_rule("", "criar_evento", evento_controller.criar, methods=["POST"])
evento_bp.add_url_rule("/<int:evento_id>", "atualizar_evento", evento_controller.atualizar, methods=["PUT"])
evento_bp.add_url_rule("/<int:evento_id>", "remover_evento", evento_controller.remover, methods=["DELETE"])
