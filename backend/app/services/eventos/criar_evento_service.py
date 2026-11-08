from sqlalchemy.exc import SQLAlchemyError

from app.models.evento import Evento
from app.repositories.evento_repository import EventoRepository
from app.services.eventos.helpers import (
    data_hora_iso,
    exigir_objeto,
    texto_opcional,
    texto_obrigatorio,
    validar_cronograma,
)
from app.utils.errors import ServiceError


def criar_evento(dados: dict):
    dados = exigir_objeto(dados)
    nome = texto_obrigatorio(dados, "nome", "Nome e obrigatorio", limite=150)
    local = texto_obrigatorio(dados, "local", "Local e obrigatorio", limite=200)

    if not dados.get("data_hora_evento"):
        raise ServiceError("Data/hora do evento e obrigatoria")
    if not dados.get("data_abertura_vendas"):
        raise ServiceError("Data de abertura das vendas e obrigatoria")

    data_hora_evento = data_hora_iso(dados.get("data_hora_evento"), "data_hora_evento")
    data_abertura_vendas = data_hora_iso(
        dados.get("data_abertura_vendas"), "data_abertura_vendas"
    )
    validar_cronograma(data_abertura_vendas, data_hora_evento)

    evento = Evento(
        nome=nome,
        descricao=texto_opcional(dados, "descricao", limite_bytes=65535),
        local=local,
        categoria=texto_opcional(dados, "categoria", limite=80),
        imagem_url=texto_opcional(dados, "imagem_url", limite=300),
        data_hora_evento=data_hora_evento,
        data_abertura_vendas=data_abertura_vendas,
    )
    try:
        return EventoRepository.salvar(evento)
    except SQLAlchemyError as erro:
        raise ServiceError("Nao foi possivel cadastrar o evento", 500) from erro
