import re

from app.utils.errors import ServiceError

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def email_valido(email: str) -> bool:
    return bool(email) and bool(EMAIL_REGEX.match(email))


def cpf_valido(cpf: str) -> bool:
    cpf = re.sub(r"\D", "", cpf or "")
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    # Calcula os dois dígitos verificadores do CPF.
    for i in [9, 10]:
        soma = 0
        for posicao in range(i):
            peso = i + 1 - posicao
            soma += int(cpf[posicao]) * peso
        digito = ((soma * 10) % 11) % 10
        if digito != int(cpf[i]):
            return False

    return True


def exigir_objeto(dados):
    if not isinstance(dados, dict):
        raise ServiceError("O corpo da requisicao deve ser um objeto JSON")
    return dados


def texto_obrigatorio(dados, campo, mensagem=None):
    valor = dados.get(campo)
    if not isinstance(valor, str) or not valor.strip():
        raise ServiceError(mensagem or f"Campo '{campo}' e obrigatorio")
    return valor.strip()


def texto_opcional(dados, campo):
    valor = dados.get(campo)
    if isinstance(valor, str) and valor.strip():
        return valor.strip()
    return None
