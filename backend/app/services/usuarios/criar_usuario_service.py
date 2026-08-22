from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.security import generate_password_hash

from app.models.usuario import Usuario
from app.services.usuarios.helpers import (
    exigir_objeto,
    normalizar_cpf,
    normalizar_email,
    texto_opcional,
    texto_obrigatorio,
    validar_senha,
)
from app.utils.errors import ServiceError


class CriarUsuarioService:
    """Caso de uso: cadastrar usuario."""

    def executar(self, dados: dict):
        dados = exigir_objeto(dados)
        nome = texto_obrigatorio(dados, "nome", "Nome e obrigatorio")
        email = normalizar_email(dados.get("email"))
        cpf = normalizar_cpf(dados.get("cpf"))
        senha = validar_senha(dados.get("senha"))

        if Usuario.buscar_por_email(email):
            raise ServiceError("Ja existe um usuario com este email", 409)
        if Usuario.buscar_por_cpf(cpf):
            raise ServiceError("Ja existe um usuario com este CPF", 409)

        usuario = Usuario(
            nome=nome,
            email=email,
            cpf=cpf,
            telefone=texto_opcional(dados, "telefone"),
            senha_hash=generate_password_hash(senha),
        )
        try:
            return usuario.salvar()
        except IntegrityError as erro:
            raise ServiceError("Email ou CPF ja cadastrado", 409) from erro
        except SQLAlchemyError as erro:
            raise ServiceError("Nao foi possivel cadastrar o usuario", 500) from erro
