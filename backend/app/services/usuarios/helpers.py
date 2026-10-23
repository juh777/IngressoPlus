import re

from app.utils.errors import ServiceError
from app.utils.converters import normalizar_booleano
from app.utils.validators import (
    cpf_valido, email_valido, exigir_objeto, texto_obrigatorio, texto_opcional,
)


def normalizar_email(valor: object) -> str:
    email = valor.strip().lower() if isinstance(valor, str) else ""
    if not email_valido(email):
        raise ServiceError("Email invalido")
    return email


def normalizar_cpf(valor: object) -> str:
    cpf = re.sub(r"\D", "", valor if isinstance(valor, str) else "")
    if not cpf_valido(cpf):
        raise ServiceError("CPF invalido")
    return cpf


def validar_senha(valor: object) -> str:
    if not isinstance(valor, str) or len(valor) < 6:
        raise ServiceError("Senha deve ter ao menos 6 caracteres")
    return valor
