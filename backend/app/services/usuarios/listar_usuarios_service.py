from app.repositories.usuario_repository import UsuarioRepository


def listar_usuarios():
    return UsuarioRepository.listar_todos()
