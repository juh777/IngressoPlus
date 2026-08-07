from datetime import datetime

from app.extensions import db


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
    criado_em = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    atualizado_em = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
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
