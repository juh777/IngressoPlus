from app.models.evento import Evento


class ListarEventosService:
    """Caso de uso: listar todos os eventos."""

    def executar(self):
        return Evento.listar_todos()
