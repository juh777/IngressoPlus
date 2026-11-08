from app.repositories.evento_repository import EventoRepository
from app.utils.errors import ServiceError


def buscar_evento(evento_id: int):
    evento = EventoRepository.buscar_por_id(evento_id)
    if not evento:
        raise ServiceError("Evento nao encontrado", 404)
    return evento
