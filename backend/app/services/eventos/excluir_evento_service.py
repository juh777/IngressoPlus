from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.repositories.evento_repository import EventoRepository
from app.utils.errors import ServiceError


def remover_evento(evento_id: int) -> None:
    evento = EventoRepository.buscar_por_id(evento_id)
    if not evento:
        raise ServiceError("Evento nao encontrado", 404)
    try:
        EventoRepository.deletar(evento)
    except IntegrityError as erro:
        raise ServiceError("Este registro possui vínculos com vendas ou outros recursos e não pode ser excluído.", 409) from erro
    except SQLAlchemyError as erro:
        raise ServiceError("Nao foi possivel excluir o evento", 500) from erro
