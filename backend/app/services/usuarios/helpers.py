import re

from app.utils.errors import ServiceError
from app.utils.converters import normalizar_booleano
from app.utils.validators import cpf_valido, email_valido


def exigir_objeto(dados: object) -> dict:
    if not isinstance(dados, dict):
        raise ServiceError("O corpo da requisicao deve ser um objeto JSON")
    return dados


def texto_obrigatorio(dados: dict, campo: str, mensagem: str | None = None) -> str:
    valor = dados.get(campo)
    texto = valor.strip() if isinstance(valor, str) else ""
    if not texto:
        raise ServiceError(mensagem or f"Campo '{campo}' e obrigatorio")
    return texto


def texto_opcional(dados: dict, campo: str) -> str | None:
    valor = dados.get(campo)
    return valor.strip() if isinstance(valor, str) and valor.strip() else None


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
