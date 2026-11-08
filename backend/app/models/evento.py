from sqlalchemy import Boolean, Column, Integer, String, Text
from sqlalchemy.dialects.mysql import DATETIME
from app.extensions import Base

class Evento(Base):
    __tablename__ = 'eventos'

    id = Column(Integer, primary_key=True)
    nome = Column(String(150), nullable=False)
    descricao = Column(Text)
    local = Column(String(200), nullable=False)
    categoria = Column(String(80))
    imagem_url = Column(String(300))
    data_hora_evento = Column(DATETIME(fsp=6), nullable=False)
    data_abertura_vendas = Column(DATETIME(fsp=6), nullable=False)
    ativo = Column(Boolean, nullable=False)
    criado_em = Column(DATETIME(fsp=6), nullable=False)
    atualizado_em = Column(DATETIME(fsp=6), nullable=False)

    def __init__(self, nome, local, data_hora_evento, data_abertura_vendas,
                 descricao=None, categoria=None, imagem_url=None, ativo=True,
                 id=None, criado_em=None, atualizado_em=None):
        self.id = id
        self.nome = nome
        self.descricao = descricao
        self.local = local
        self.categoria = categoria
        self.imagem_url = imagem_url
        self.data_hora_evento = data_hora_evento
        self.data_abertura_vendas = data_abertura_vendas
        self.ativo = bool(ativo)
        self.criado_em = criado_em
        self.atualizado_em = atualizado_em

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'local': self.local,
            'categoria': self.categoria,
            'imagem_url': self.imagem_url,
            'data_hora_evento': self.data_hora_evento.isoformat(),
            'data_abertura_vendas': self.data_abertura_vendas.isoformat(),
            'ativo': self.ativo,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None,
        }
