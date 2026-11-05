from functools import wraps

from app.services.conta_service import usuario_atual
from app.utils.errors import ServiceError


def exigir_login(funcao):
    @wraps(funcao)
    def verificar(*args, **kwargs):
        usuario_atual()
        return funcao(*args, **kwargs)
    return verificar


def exigir_admin(funcao):
    @wraps(funcao)
    def verificar(*args, **kwargs):
        if usuario_atual()['papel'] != 'admin':
            raise ServiceError('Esta ação é exclusiva do administrador.', 403)
        return funcao(*args, **kwargs)
    return verificar
