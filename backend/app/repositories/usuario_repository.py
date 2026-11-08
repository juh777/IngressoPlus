from sqlalchemy import select
from app.extensions import consultar, obter_sessao
from app.models.usuario import Usuario
from app.utils.vendas import agora

class UsuarioRepository:
    @staticmethod
    def listar_todos():
        with obter_sessao() as sessao:
            return list(sessao.scalars(select(Usuario).order_by(Usuario.nome)))

    @staticmethod
    def buscar_por_id(usuario_id):
        with obter_sessao() as sessao:
            return sessao.get(Usuario, usuario_id)

    @staticmethod
    def buscar_por_email(email):
        with obter_sessao() as sessao:
            return sessao.scalar(select(Usuario).where(Usuario.email == email))

    @staticmethod
    def buscar_por_cpf(cpf):
        with obter_sessao() as sessao:
            return sessao.scalar(select(Usuario).where(Usuario.cpf == cpf))

    @staticmethod
    def salvar(usuario):
        usuario.atualizado_em = agora()
        if usuario.id is None:
            usuario.criado_em = usuario.atualizado_em
        with obter_sessao() as sessao, sessao.begin():
            sessao.add(usuario)
        return usuario

    @staticmethod
    def deletar(usuario):
        with obter_sessao() as sessao, sessao.begin():
            sessao.delete(usuario)

    @staticmethod
    def buscar_sessao(usuario_id):
        return consultar(
            'SELECT id, nome, email, cpf, telefone, papel, ativo FROM usuarios WHERE id = %s',
            (usuario_id,), apenas_um=True,
        )

    @staticmethod
    def buscar_por_termo(termo):
        padrao = '%' + termo.strip() + '%'
        linhas = consultar(
            """SELECT * FROM usuarios
               WHERE LOWER(nome) LIKE LOWER(%s) OR LOWER(email) LIKE LOWER(%s)
               ORDER BY nome""",
            (padrao, padrao),
        )
        return [Usuario(**linha) for linha in linhas]
