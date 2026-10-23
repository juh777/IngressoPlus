from pymysql import MySQLError

from app.models.evento import Evento
from app.services.eventos.helpers import (
    data_hora_iso,
    exigir_objeto,
    texto_opcional,
    texto_obrigatorio,
    validar_cronograma,
)
from app.utils.converters import normalizar_booleano
from app.utils.errors import ServiceError


def atualizar_evento(evento_id: int, dados: dict):
    dados = exigir_objeto(dados)
    evento = Evento.buscar_por_id(evento_id)
    if not evento:
        raise ServiceError("Evento nao encontrado", 404)

    if "nome" in dados:
        evento.nome = texto_obrigatorio(dados, "nome", "Nome e obrigatorio")
    if "local" in dados:
        evento.local = texto_obrigatorio(dados, "local", "Local e obrigatorio")
    if "descricao" in dados:
        evento.descricao = texto_opcional(dados, "descricao")
    if "categoria" in dados:
        evento.categoria = texto_opcional(dados, "categoria")
    if "imagem_url" in dados:
        evento.imagem_url = texto_opcional(dados, "imagem_url")
    if "data_hora_evento" in dados:
        evento.data_hora_evento = data_hora_iso(
            dados.get("data_hora_evento"), "data_hora_evento"
        )
    if "data_abertura_vendas" in dados:
        evento.data_abertura_vendas = data_hora_iso(
            dados.get("data_abertura_vendas"), "data_abertura_vendas"
        )
    if "ativo" in dados:
        evento.ativo = normalizar_booleano(dados.get("ativo"))

    validar_cronograma(evento.data_abertura_vendas, evento.data_hora_evento)
    try:
        return evento.atualizar()
    except MySQLError as erro:
        raise ServiceError("Nao foi possivel atualizar o evento", 500) from erro
