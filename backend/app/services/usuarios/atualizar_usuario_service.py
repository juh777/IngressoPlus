from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.security import generate_password_hash

from app.models.usuario import Usuario
from app.services.usuarios.helpers import (
    exigir_objeto,
    normalizar_booleano,
    normalizar_cpf,
    normalizar_email,
    texto_opcional,
    texto_obrigatorio,
    validar_senha,
)
from app.utils.errors import ServiceError


class AtualizarUsuarioService:
    """Caso de uso: atualizar os dados de um usuario."""

    def executar(self, usuario_id: int, dados: dict):
        dados = exigir_objeto(dados)
        usuario = Usuario.buscar_por_id(usuario_id)
        if not usuario:
            raise ServiceError("Usuario nao encontrado", 404)

        if "nome" in dados:
            usuario.nome = texto_obrigatorio(dados, "nome", "Nome e obrigatorio")

        if "email" in dados:
            email = normalizar_email(dados.get("email"))
            existente = Usuario.buscar_por_email(email)
            if existente and existente.id != usuario.id:
                raise ServiceError("Ja existe um usuario com este email", 409)
            usuario.email = email

        if "cpf" in dados:
            cpf = normalizar_cpf(dados.get("cpf"))
            existente = Usuario.buscar_por_cpf(cpf)
            if existente and existente.id != usuario.id:
                raise ServiceError("Ja existe um usuario com este CPF", 409)
            usuario.cpf = cpf

        if "telefone" in dados:
            usuario.telefone = texto_opcional(dados, "telefone")

        if "senha" in dados:
            usuario.senha_hash = generate_password_hash(validar_senha(dados.get("senha")))

        if "ativo" in dados:
            usuario.ativo = normalizar_booleano(dados.get("ativo"))

        try:
            return usuario.atualizar()
        except IntegrityError as erro:
            raise ServiceError("Email ou CPF ja cadastrado", 409) from erro
        except SQLAlchemyError as erro:
            raise ServiceError("Nao foi possivel atualizar o usuario", 500) from erro
