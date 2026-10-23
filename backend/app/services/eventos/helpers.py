from datetime import datetime, timezone

from app.utils.errors import ServiceError
from app.utils.validators import exigir_objeto, texto_obrigatorio, texto_opcional


def data_hora_iso(valor: object, campo: str) -> datetime:
    if not isinstance(valor, str):
        raise ServiceError(f"Campo '{campo}' deve ser uma data/hora valida (ISO 8601)")
    try:
        data_hora = datetime.fromisoformat(valor.replace("Z", "+00:00"))
        # O MySQL guarda datas sem fuso. Convertemos entradas com fuso para UTC.
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
