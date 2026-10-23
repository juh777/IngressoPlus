from app.models.evento import Evento


def listar_eventos():
    return Evento.listar_todos()
