from app.models.usuario import Usuario
from app.utils.errors import ServiceError


class BuscarUsuarioService:
    """Caso de uso: buscar um usuario por identificador."""

    def executar(self, usuario_id: int):
        usuario = Usuario.buscar_por_id(usuario_id)
        if not usuario:
            raise ServiceError("Usuario nao encontrado", 404)
        return usuario
