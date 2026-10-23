from app.models.usuario import Usuario


def listar_usuarios():
    return Usuario.listar_todos()
