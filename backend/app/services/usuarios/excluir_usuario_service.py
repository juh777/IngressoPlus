from sqlalchemy.exc import SQLAlchemyError

from app.models.usuario import Usuario
from app.utils.errors import ServiceError


class ExcluirUsuarioService:
    """Caso de uso: excluir usuario."""

    def executar(self, usuario_id: int) -> None:
        usuario = Usuario.buscar_por_id(usuario_id)
        if not usuario:
            raise ServiceError("Usuario nao encontrado", 404)
        try:
            usuario.deletar()
        except SQLAlchemyError as erro:
            raise ServiceError("Nao foi possivel excluir o usuario", 500) from erro
