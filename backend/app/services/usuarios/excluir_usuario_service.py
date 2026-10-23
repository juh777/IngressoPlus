from pymysql import IntegrityError, MySQLError

from app.models.usuario import Usuario
from app.utils.errors import ServiceError


def remover_usuario(usuario_id: int) -> None:
    usuario = Usuario.buscar_por_id(usuario_id)
    if not usuario:
        raise ServiceError("Usuario nao encontrado", 404)
    try:
        usuario.deletar()
    except IntegrityError as erro:
        raise ServiceError("Este registro possui vínculos com vendas ou outros recursos e não pode ser excluído.", 409) from erro
    except MySQLError as erro:
        raise ServiceError("Nao foi possivel excluir o usuario", 500) from erro
