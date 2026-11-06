from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.security import generate_password_hash

from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository
from app.services.usuarios.helpers import (
    exigir_objeto,
    normalizar_cpf,
    normalizar_email,
    texto_opcional,
    texto_obrigatorio,
    validar_senha,
)
from app.utils.errors import ServiceError


def criar_usuario(dados: dict):
    dados = exigir_objeto(dados)
    nome = texto_obrigatorio(dados, "nome", "Nome e obrigatorio", limite=150)
    email = normalizar_email(dados.get("email"))
    cpf = normalizar_cpf(dados.get("cpf"))
    senha = validar_senha(dados.get("senha"))

    if UsuarioRepository.buscar_por_email(email):
        raise ServiceError("Ja existe um usuario com este email", 409)
    if UsuarioRepository.buscar_por_cpf(cpf):
        raise ServiceError("Ja existe um usuario com este CPF", 409)

    usuario = Usuario(
        nome=nome,
        email=email,
        cpf=cpf,
        telefone=texto_opcional(dados, "telefone", limite=20),
        senha_hash=generate_password_hash(senha),
    )
    try:
        return UsuarioRepository.salvar(usuario)
    except IntegrityError as erro:
        raise ServiceError("Email ou CPF ja cadastrado", 409) from erro
    except SQLAlchemyError as erro:
        raise ServiceError("Nao foi possivel cadastrar o usuario", 500) from erro
