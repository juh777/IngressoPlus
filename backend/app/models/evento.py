from datetime import datetime, timezone
from app.extensions import consultar, executar

class Evento:
    """Dados de um evento e seu CRUD em SQL puro."""

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

    @staticmethod
    def listar_todos():
        linhas = consultar('SELECT * FROM eventos ORDER BY data_hora_evento')
        return [Evento(**linha) for linha in linhas]

    @staticmethod
    def buscar_por_id(evento_id):
        linha = consultar('SELECT * FROM eventos WHERE id = %s', (evento_id,), apenas_um=True)
        return Evento(**linha) if linha else None

    def salvar(self):
        agora = datetime.now(timezone.utc).replace(tzinfo=None)
        self.id = executar(
            """INSERT INTO eventos
               (nome, descricao, `local`, categoria, imagem_url, data_hora_evento,
                data_abertura_vendas, ativo, criado_em, atualizado_em)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (self.nome, self.descricao, self.local, self.categoria, self.imagem_url,
             self.data_hora_evento, self.data_abertura_vendas, self.ativo, agora, agora),
        )
        self.criado_em = agora
        self.atualizado_em = agora
        return self

    def atualizar(self):
        agora = datetime.now(timezone.utc).replace(tzinfo=None)
        executar(
            """UPDATE eventos SET nome = %s, descricao = %s, `local` = %s,
               categoria = %s, imagem_url = %s, data_hora_evento = %s,
               data_abertura_vendas = %s, ativo = %s, atualizado_em = %s
               WHERE id = %s""",
            (self.nome, self.descricao, self.local, self.categoria, self.imagem_url,
             self.data_hora_evento, self.data_abertura_vendas, self.ativo, agora, self.id),
        )
        self.atualizado_em = agora
        return self

    def deletar(self):
        executar('DELETE FROM eventos WHERE id = %s', (self.id,))
