"""Consultas especializadas que nao pertencem ao CRUD dos models."""

from app.repositories.evento_repository import EventoRepository
from app.repositories.usuario_repository import UsuarioRepository

__all__ = ["EventoRepository", "UsuarioRepository"]
