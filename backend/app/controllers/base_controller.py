from flask import jsonify

from app.utils.errors import ServiceError


class BaseController:
    """Responsabilidade HTTP comum aos controllers da API."""

    @staticmethod
    def responder_erro(erro: ServiceError):
        return jsonify({"erro": erro.message}), erro.status_code
