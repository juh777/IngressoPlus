from datetime import datetime, timezone

from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db


def _agora_utc_sem_timezone():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Evento(db.Model):
    __tablename__ = "eventos"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    local = db.Column(db.String(200), nullable=False)
    categoria = db.Column(db.String(80), nullable=True)
    imagem_url = db.Column(db.String(300), nullable=True)
    data_hora_evento = db.Column(db.DateTime, nullable=False)
    data_abertura_vendas = db.Column(db.DateTime, nullable=False)
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
            "descricao": self.descricao,
            "local": self.local,
            "categoria": self.categoria,
            "imagem_url": self.imagem_url,
            "data_hora_evento": self.data_hora_evento.isoformat()
            if self.data_hora_evento
            else None,
            "data_abertura_vendas": self.data_abertura_vendas.isoformat()
            if self.data_abertura_vendas
            else None,
            "ativo": self.ativo,
            "criado_em": self.criado_em.isoformat() if self.criado_em else None,
            "atualizado_em": self.atualizado_em.isoformat() if self.atualizado_em else None,
        }

    # Operacoes CRUD convencionais pertencem ao proprio Model. Consultas de
    # filtro compostas ficam no repository do recurso.
    @classmethod
    def listar_todos(cls):
        consulta = db.select(cls).order_by(cls.data_hora_evento.asc())
        return list(db.session.scalars(consulta).all())

    @classmethod
    def buscar_por_id(cls, evento_id: int):
        return db.session.get(cls, evento_id)

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
