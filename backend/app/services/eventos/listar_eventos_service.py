from app.repositories.evento_repository import EventoRepository


def listar_eventos():
    return EventoRepository.listar_todos()
