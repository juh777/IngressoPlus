from sqlalchemy import select
from app.extensions import consultar, obter_sessao
from app.models.evento import Evento
from app.utils.vendas import agora

class EventoRepository:
    @staticmethod
    def listar_todos():
        with obter_sessao() as sessao:
            return list(sessao.scalars(select(Evento).order_by(Evento.data_hora_evento)))

    @staticmethod
    def buscar_por_id(evento_id):
        with obter_sessao() as sessao:
            return sessao.get(Evento, evento_id)

    @staticmethod
    def salvar(evento):
        evento.atualizado_em = agora()
        if evento.id is None:
            evento.criado_em = evento.atualizado_em
        with obter_sessao() as sessao, sessao.begin():
            sessao.add(evento)
        return evento

    @staticmethod
    def deletar(evento):
        with obter_sessao() as sessao, sessao.begin():
            sessao.delete(evento)

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

    @staticmethod
    def listar_para_recomendacao(agora):
        return consultar('''SELECT id, nome, categoria, `local`, data_hora_evento FROM eventos
                            WHERE ativo = TRUE AND data_hora_evento > %s ORDER BY data_hora_evento''', (agora,))
