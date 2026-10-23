from datetime import datetime, timezone
from app.extensions import consultar, executar

class Usuario:
    """Dados de um usuário e seu CRUD em SQL puro."""

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

    @staticmethod
    def listar_todos():
        linhas = consultar('SELECT * FROM usuarios ORDER BY nome')
        return [Usuario(**linha) for linha in linhas]

    @staticmethod
    def buscar_por_id(usuario_id):
        linha = consultar('SELECT * FROM usuarios WHERE id = %s', (usuario_id,), apenas_um=True)
        return Usuario(**linha) if linha else None

    @staticmethod
    def buscar_por_email(email):
        linha = consultar('SELECT * FROM usuarios WHERE email = %s', (email,), apenas_um=True)
        return Usuario(**linha) if linha else None

    @staticmethod
    def buscar_por_cpf(cpf):
        linha = consultar('SELECT * FROM usuarios WHERE cpf = %s', (cpf,), apenas_um=True)
        return Usuario(**linha) if linha else None

    def salvar(self):
        agora = datetime.now(timezone.utc).replace(tzinfo=None)
        self.id = executar(
            """INSERT INTO usuarios
               (nome, email, cpf, telefone, senha_hash, ativo, criado_em, atualizado_em)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (self.nome, self.email, self.cpf, self.telefone, self.senha_hash,
             self.ativo, agora, agora),
        )
        self.criado_em = agora
        self.atualizado_em = agora
        return self

    def atualizar(self):
        agora = datetime.now(timezone.utc).replace(tzinfo=None)
        executar(
            """UPDATE usuarios SET nome = %s, email = %s, cpf = %s,
               telefone = %s, senha_hash = %s, ativo = %s, atualizado_em = %s
               WHERE id = %s""",
            (self.nome, self.email, self.cpf, self.telefone, self.senha_hash,
             self.ativo, agora, self.id),
        )
        self.atualizado_em = agora
        return self

    def deletar(self):
        executar('DELETE FROM usuarios WHERE id = %s', (self.id,))
