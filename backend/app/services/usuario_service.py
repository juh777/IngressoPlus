import re

from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models.usuario import Usuario
from app.utils.errors import ServiceError
from app.utils.validators import cpf_valido, email_valido


def listar_usuarios():
    return Usuario.query.order_by(Usuario.nome).all()


def buscar_usuario(usuario_id: int) -> Usuario:
    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        raise ServiceError("Usuario nao encontrado", 404)
    return usuario


def criar_usuario(dados: dict) -> Usuario:
    nome = (dados.get("nome") or "").strip()
    email = (dados.get("email") or "").strip().lower()
    cpf = re.sub(r"\D", "", dados.get("cpf") or "")
    senha = dados.get("senha") or ""
    telefone = (dados.get("telefone") or "").strip() or None

    if not nome:
        raise ServiceError("Nome e obrigatorio")
    if not email_valido(email):
        raise ServiceError("Email invalido")
    if not cpf_valido(cpf):
        raise ServiceError("CPF invalido")
    if len(senha) < 6:
        raise ServiceError("Senha deve ter ao menos 6 caracteres")

    if Usuario.query.filter_by(email=email).first():
        raise ServiceError("Ja existe um usuario com este email", 409)
    if Usuario.query.filter_by(cpf=cpf).first():
        raise ServiceError("Ja existe um usuario com este CPF", 409)

    usuario = Usuario(
        nome=nome,
        email=email,
        cpf=cpf,
        telefone=telefone,
        senha_hash=generate_password_hash(senha),
    )
    db.session.add(usuario)
    db.session.commit()
    return usuario


def atualizar_usuario(usuario_id: int, dados: dict) -> Usuario:
    usuario = buscar_usuario(usuario_id)

    if "nome" in dados:
        nome = (dados.get("nome") or "").strip()
        if not nome:
            raise ServiceError("Nome e obrigatorio")
        usuario.nome = nome

    if "email" in dados:
        email = (dados.get("email") or "").strip().lower()
        if not email_valido(email):
            raise ServiceError("Email invalido")
        existente = Usuario.query.filter_by(email=email).first()
        if existente and existente.id != usuario.id:
            raise ServiceError("Ja existe um usuario com este email", 409)
        usuario.email = email

    if "cpf" in dados:
        cpf = re.sub(r"\D", "", dados.get("cpf") or "")
        if not cpf_valido(cpf):
            raise ServiceError("CPF invalido")
        existente = Usuario.query.filter_by(cpf=cpf).first()
        if existente and existente.id != usuario.id:
            raise ServiceError("Ja existe um usuario com este CPF", 409)
        usuario.cpf = cpf

    if "telefone" in dados:
        usuario.telefone = (dados.get("telefone") or "").strip() or None

    if "senha" in dados and dados["senha"]:
        if len(dados["senha"]) < 6:
            raise ServiceError("Senha deve ter ao menos 6 caracteres")
        usuario.senha_hash = generate_password_hash(dados["senha"])

    if "ativo" in dados:
        usuario.ativo = bool(dados["ativo"])

    db.session.commit()
    return usuario


def remover_usuario(usuario_id: int) -> None:
    usuario = buscar_usuario(usuario_id)
    db.session.delete(usuario)
    db.session.commit()
