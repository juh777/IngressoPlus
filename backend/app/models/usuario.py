from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.dialects.mysql import DATETIME
from app.extensions import Base

class Usuario(Base):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True)
    nome = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    cpf = Column(String(11), nullable=False, unique=True)
    telefone = Column(String(20))
    senha_hash = Column(String(255), nullable=False)
    ativo = Column(Boolean, nullable=False)
    papel = Column(String(20), nullable=False)
    criado_em = Column(DATETIME(fsp=6), nullable=False)
    atualizado_em = Column(DATETIME(fsp=6), nullable=False)

    def __init__(self, nome, email, cpf, senha_hash, telefone=None,
                 ativo=True, id=None, criado_em=None, atualizado_em=None, papel='cliente'):
        self.id = id
        self.nome = nome
        self.email = email
        self.cpf = cpf
        self.telefone = telefone
        self.senha_hash = senha_hash
        self.ativo = bool(ativo)
        self.papel = papel
        self.criado_em = criado_em
        self.atualizado_em = atualizado_em

    def to_dict(self):
        # O hash da senha nunca é enviado para a interface.
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'cpf': self.cpf,
            'telefone': self.telefone,
            'ativo': self.ativo,
            'papel': self.papel,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None,
        }
