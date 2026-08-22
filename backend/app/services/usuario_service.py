"""Compatibilidade com importacoes antigas; a logica mora nas classes de caso de uso."""

from app.services.usuarios import (
    AtualizarUsuarioService,
    BuscarUsuarioService,
    CriarUsuarioService,
    ExcluirUsuarioService,
    ListarUsuariosService,
)

listar_usuarios = ListarUsuariosService().executar
buscar_usuario = BuscarUsuarioService().executar
criar_usuario = CriarUsuarioService().executar
atualizar_usuario = AtualizarUsuarioService().executar
remover_usuario = ExcluirUsuarioService().executar
