from datetime import datetime, timezone

from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db


def _agora_utc_sem_timezone():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    cpf = db.Column(db.String(11), nullable=False, unique=True)
    telefone = db.Column(db.String(20), nullable=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    criado_em = db.Column(db.DateTime, nullable=False, default=_agora_utc_sem_timezone)
    atualizado_em = db.Column(
        db.DateTime,
        nullable=False,
        default=_agora_utc_sem_timezone,
        onupdate=_agora_utc_sem_timezone,
    )

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "cpf": self.cpf,
            "telefone": self.telefone,
            "ativo": self.ativo,
            "criado_em": self.criado_em.isoformat() if self.criado_em else None,
            "atualizado_em": self.atualizado_em.isoformat() if self.atualizado_em else None,
        }

    # Operacoes CRUD convencionais pertencem ao proprio Model. Consultas de
    # busca/filtro que fogem do CRUD ficam nos repositories.
    @classmethod
    def listar_todos(cls):
        consulta = db.select(cls).order_by(cls.nome.asc())
        return list(db.session.scalars(consulta).all())

    @classmethod
    def buscar_por_id(cls, usuario_id: int):
        return db.session.get(cls, usuario_id)

    @classmethod
    def buscar_por_email(cls, email: str):
        return db.session.scalar(db.select(cls).filter_by(email=email))

    @classmethod
    def buscar_por_cpf(cls, cpf: str):
        return db.session.scalar(db.select(cls).filter_by(cpf=cpf))

    def salvar(self):
        db.session.add(self)
        return self._confirmar_transacao()

    def atualizar(self):
        db.session.add(self)
        return self._confirmar_transacao()

    def deletar(self) -> None:
        db.session.delete(self)
        self._confirmar_transacao()

    def _confirmar_transacao(self):
        try:
            db.session.commit()
            return self
        except SQLAlchemyError:
            db.session.rollback()
            raise
