from sqlalchemy import select

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
