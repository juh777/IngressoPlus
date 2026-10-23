from app.repositories.usuario_repository import UsuarioRepository
from app.utils.errors import ServiceError


def buscar_usuarios_por_termo(termo: str | None):
    termo_normalizado = termo.strip() if isinstance(termo, str) else ""
    if not termo_normalizado:
        raise ServiceError("O parametro 'termo' e obrigatorio")
    return UsuarioRepository.buscar_por_termo(termo_normalizado)
