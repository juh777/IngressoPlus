from app.models.evento import Evento
from app.utils.errors import ServiceError


class BuscarEventoService:
    """Caso de uso: buscar um evento por identificador."""

    def executar(self, evento_id: int):
        evento = Evento.buscar_por_id(evento_id)
        if not evento:
            raise ServiceError("Evento nao encontrado", 404)
        return evento
