from sqlalchemy import or_, select

from app.extensions import db
from app.models.usuario import Usuario


class UsuarioRepository:
    """Consultas especiais do recurso Usuario."""

    @staticmethod
    def buscar_por_termo(termo: str) -> list[Usuario]:
        """Busca por nome ou e-mail sem diferenciar maiusculas/minusculas."""
        padrao = f"%{termo.strip()}%"
        consulta = (
            select(Usuario)
            .where(
                or_(
                    Usuario.nome.ilike(padrao),
                    Usuario.email.ilike(padrao),
                )
            )
            .order_by(Usuario.nome.asc())
        )
        return list(db.session.scalars(consulta).all())
