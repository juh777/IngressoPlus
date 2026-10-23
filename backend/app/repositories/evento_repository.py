from app.extensions import consultar
from app.models.evento import Evento

class EventoRepository:
    @staticmethod
    def filtrar(categoria=None, local=None, status=None):
        sql = 'SELECT * FROM eventos WHERE 1 = 1'
        parametros = []

        # Só acrescentamos condições fixas. Os valores vão separados.
        if categoria:
            sql += ' AND LOWER(categoria) LIKE LOWER(%s)'
            parametros.append('%' + categoria.strip() + '%')
        if local:
            sql += ' AND LOWER(`local`) LIKE LOWER(%s)'
            parametros.append('%' + local.strip() + '%')
        if status is not None:
            sql += ' AND ativo = %s'
            parametros.append(status)

        sql += ' ORDER BY data_hora_evento'
        linhas = consultar(sql, parametros)
        return [Evento(**linha) for linha in linhas]

    @staticmethod
    def gerar_relatorio_por_categoria_status():
        return consultar(
            """SELECT categoria, ativo, COUNT(*) AS total FROM eventos
               GROUP BY categoria, ativo ORDER BY categoria, ativo DESC"""
        )
