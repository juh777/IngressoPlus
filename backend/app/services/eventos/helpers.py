from datetime import datetime, timezone

from app.utils.errors import ServiceError


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


def data_hora_iso(valor: object, campo: str) -> datetime:
    if not isinstance(valor, str):
        raise ServiceError(f"Campo '{campo}' deve ser uma data/hora valida (ISO 8601)")
    try:
        data_hora = datetime.fromisoformat(valor.replace("Z", "+00:00"))
        # As colunas atuais sao DateTime sem timezone. Normalizar entradas
        # conscientes de timezone para UTC-naive evita comparacoes ambiguas.
        if data_hora.tzinfo is not None:
            data_hora = data_hora.astimezone(timezone.utc).replace(tzinfo=None)
        return data_hora
    except ValueError as erro:
        raise ServiceError(
            f"Campo '{campo}' deve ser uma data/hora valida (ISO 8601)"
        ) from erro


def validar_cronograma(data_abertura_vendas: datetime, data_hora_evento: datetime) -> None:
    if data_abertura_vendas > data_hora_evento:
        raise ServiceError("A abertura das vendas deve ser antes do evento")
