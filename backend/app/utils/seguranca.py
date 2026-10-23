from functools import wraps

from flask import session
from app.extensions import consultar
from app.utils.errors import ServiceError


def usuario_atual():
    usuario_id = session.get('usuario_id')
    usuario = consultar(
        'SELECT id, nome, email, cpf, telefone, papel, ativo FROM usuarios WHERE id = %s',
        (usuario_id,), apenas_um=True,
    ) if usuario_id else None
    if not usuario or not usuario['ativo']:
        raise ServiceError('Entre na sua conta para continuar.', 401)
    return usuario


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
