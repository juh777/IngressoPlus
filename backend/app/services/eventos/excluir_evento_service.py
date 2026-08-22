from sqlalchemy.exc import SQLAlchemyError

from app.models.evento import Evento
from app.utils.errors import ServiceError


class ExcluirEventoService:
    """Caso de uso: excluir evento."""

    def executar(self, evento_id: int) -> None:
        evento = Evento.buscar_por_id(evento_id)
        if not evento:
            raise ServiceError("Evento nao encontrado", 404)
        try:
            evento.deletar()
        except SQLAlchemyError as erro:
            raise ServiceError("Nao foi possivel excluir o evento", 500) from erro
