"""Compatibilidade com importacoes antigas; a logica mora nas classes de caso de uso."""

from app.services.eventos import (
    AtualizarEventoService,
    BuscarEventoService,
    CriarEventoService,
    ExcluirEventoService,
    ListarEventosService,
)

listar_eventos = ListarEventosService().executar
buscar_evento = BuscarEventoService().executar
criar_evento = CriarEventoService().executar
atualizar_evento = AtualizarEventoService().executar
remover_evento = ExcluirEventoService().executar
