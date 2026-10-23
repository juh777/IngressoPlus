from app.extensions import consultar
from app.models.usuario import Usuario

class UsuarioRepository:
    @staticmethod
    def buscar_por_termo(termo):
        padrao = '%' + termo.strip() + '%'
        linhas = consultar(
            """SELECT * FROM usuarios
               WHERE LOWER(nome) LIKE LOWER(%s) OR LOWER(email) LIKE LOWER(%s)
               ORDER BY nome""",
            (padrao, padrao),
        )
        return [Usuario(**linha) for linha in linhas]
