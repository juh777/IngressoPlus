from flask import Blueprint, jsonify, request

from app.controllers.base_controller import BaseController
from app.services.usuarios import (
    AtualizarUsuarioService,
    BuscarUsuarioService,
    BuscarUsuariosPorTermoService,
    CriarUsuarioService,
    ExcluirUsuarioService,
    ListarUsuariosService,
)
from app.utils.errors import ServiceError

usuario_bp = Blueprint("usuarios", __name__)


class UsuarioController(BaseController):
    """Controller HTTP do recurso Usuario; regras ficam nos services."""

    def __init__(self):
        self.listar_service = ListarUsuariosService()
        self.buscar_service = BuscarUsuarioService()
        self.buscar_por_termo_service = BuscarUsuariosPorTermoService()
        self.criar_service = CriarUsuarioService()
        self.atualizar_service = AtualizarUsuarioService()
        self.excluir_service = ExcluirUsuarioService()

    def listar(self):
        try:
            usuarios = self.listar_service.executar()
            return jsonify([usuario.to_dict() for usuario in usuarios])
        except ServiceError as erro:
            return self.responder_erro(erro)

    def buscar(self, usuario_id: int):
        try:
            usuario = self.buscar_service.executar(usuario_id)
            return jsonify(usuario.to_dict())
        except ServiceError as erro:
            return self.responder_erro(erro)

    def buscar_por_termo(self):
        try:
            usuarios = self.buscar_por_termo_service.executar(request.args.get("termo"))
            return jsonify([usuario.to_dict() for usuario in usuarios])
        except ServiceError as erro:
            return self.responder_erro(erro)

    def criar(self):
        dados = request.get_json(silent=True) or {}
        try:
            usuario = self.criar_service.executar(dados)
            return jsonify(usuario.to_dict()), 201
        except ServiceError as erro:
            return self.responder_erro(erro)

    def atualizar(self, usuario_id: int):
        dados = request.get_json(silent=True) or {}
        try:
            usuario = self.atualizar_service.executar(usuario_id, dados)
            return jsonify(usuario.to_dict())
        except ServiceError as erro:
            return self.responder_erro(erro)

    def remover(self, usuario_id: int):
        try:
            self.excluir_service.executar(usuario_id)
            return "", 204
        except ServiceError as erro:
            return self.responder_erro(erro)


usuario_controller = UsuarioController()
usuario_bp.add_url_rule("", "listar_usuarios", usuario_controller.listar, methods=["GET"])
usuario_bp.add_url_rule("/busca", "buscar_usuarios_por_termo", usuario_controller.buscar_por_termo, methods=["GET"])
usuario_bp.add_url_rule("/<int:usuario_id>", "buscar_usuario", usuario_controller.buscar, methods=["GET"])
usuario_bp.add_url_rule("", "criar_usuario", usuario_controller.criar, methods=["POST"])
usuario_bp.add_url_rule("/<int:usuario_id>", "atualizar_usuario", usuario_controller.atualizar, methods=["PUT"])
usuario_bp.add_url_rule("/<int:usuario_id>", "remover_usuario", usuario_controller.remover, methods=["DELETE"])
