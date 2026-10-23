from app.models.evento import Evento
from app.utils.errors import ServiceError


def buscar_evento(evento_id: int):
    evento = Evento.buscar_por_id(evento_id)
    if not evento:
        raise ServiceError("Evento nao encontrado", 404)
    return evento
