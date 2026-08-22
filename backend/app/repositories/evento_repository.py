from sqlalchemy import func, select

from app.extensions import db
from app.models.evento import Evento


class EventoRepository:
    """Consultas compostas do recurso Evento."""

    @staticmethod
    def filtrar(
        categoria: str | None = None,
        local: str | None = None,
        status: bool | None = None,
    ) -> list[Evento]:
        consulta = select(Evento)

        if categoria:
            consulta = consulta.where(Evento.categoria.ilike(f"%{categoria.strip()}%"))
        if local:
            consulta = consulta.where(Evento.local.ilike(f"%{local.strip()}%"))
        if status is not None:
            consulta = consulta.where(Evento.ativo.is_(status))

        consulta = consulta.order_by(Evento.data_hora_evento.asc())
        return list(db.session.scalars(consulta).all())

    @staticmethod
    def gerar_relatorio_por_categoria_status():
        """Agrupa eventos por categoria e situação para o relatório gerencial."""
        consulta = (
            select(
                Evento.categoria.label("categoria"),
                Evento.ativo.label("ativo"),
                func.count(Evento.id).label("total"),
            )
            .group_by(Evento.categoria, Evento.ativo)
            .order_by(Evento.categoria.asc(), Evento.ativo.desc())
        )
        return list(db.session.execute(consulta).all())
