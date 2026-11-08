from app.repositories.usuario_repository import UsuarioRepository
from app.utils.errors import ServiceError


def buscar_usuario(usuario_id: int):
    usuario = UsuarioRepository.buscar_por_id(usuario_id)
    if not usuario:
        raise ServiceError("Usuario nao encontrado", 404)
    return usuario
