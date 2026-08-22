from app.models.usuario import Usuario


class ListarUsuariosService:
    """Caso de uso: listar todos os usuarios."""

    def executar(self):
        return Usuario.listar_todos()
