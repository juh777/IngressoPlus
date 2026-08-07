from datetime import datetime

from app.extensions import db
from app.models.evento import Evento
from app.utils.errors import ServiceError


def _parse_datetime(valor: str, campo: str) -> datetime:
    try:
        return datetime.fromisoformat(valor)
    except (TypeError, ValueError):
        raise ServiceError(f"Campo '{campo}' deve ser uma data/hora valida (ISO 8601)")


def listar_eventos():
    return Evento.query.order_by(Evento.data_hora_evento).all()


def buscar_evento(evento_id: int) -> Evento:
    evento = Evento.query.get(evento_id)
    if not evento:
        raise ServiceError("Evento nao encontrado", 404)
    return evento


def criar_evento(dados: dict) -> Evento:
    nome = (dados.get("nome") or "").strip()
    local = (dados.get("local") or "").strip()

    if not nome:
        raise ServiceError("Nome e obrigatorio")
    if not local:
        raise ServiceError("Local e obrigatorio")
    if not dados.get("data_hora_evento"):
        raise ServiceError("Data/hora do evento e obrigatoria")
    if not dados.get("data_abertura_vendas"):
        raise ServiceError("Data de abertura das vendas e obrigatoria")

    data_hora_evento = _parse_datetime(dados["data_hora_evento"], "data_hora_evento")
    data_abertura_vendas = _parse_datetime(
        dados["data_abertura_vendas"], "data_abertura_vendas"
    )

    if data_abertura_vendas > data_hora_evento:
        raise ServiceError("A abertura das vendas deve ser antes do evento")

    evento = Evento(
        nome=nome,
        descricao=(dados.get("descricao") or "").strip() or None,
        local=local,
        categoria=(dados.get("categoria") or "").strip() or None,
        imagem_url=(dados.get("imagem_url") or "").strip() or None,
        data_hora_evento=data_hora_evento,
        data_abertura_vendas=data_abertura_vendas,
    )
    db.session.add(evento)
    db.session.commit()
    return evento


def atualizar_evento(evento_id: int, dados: dict) -> Evento:
    evento = buscar_evento(evento_id)

    if "nome" in dados:
        nome = (dados.get("nome") or "").strip()
        if not nome:
            raise ServiceError("Nome e obrigatorio")
        evento.nome = nome

    if "local" in dados:
        local = (dados.get("local") or "").strip()
        if not local:
            raise ServiceError("Local e obrigatorio")
        evento.local = local

    if "descricao" in dados:
        evento.descricao = (dados.get("descricao") or "").strip() or None

    if "categoria" in dados:
        evento.categoria = (dados.get("categoria") or "").strip() or None

    if "imagem_url" in dados:
        evento.imagem_url = (dados.get("imagem_url") or "").strip() or None

    if "data_hora_evento" in dados:
        evento.data_hora_evento = _parse_datetime(
            dados["data_hora_evento"], "data_hora_evento"
        )

    if "data_abertura_vendas" in dados:
        evento.data_abertura_vendas = _parse_datetime(
            dados["data_abertura_vendas"], "data_abertura_vendas"
        )

    if evento.data_abertura_vendas > evento.data_hora_evento:
        raise ServiceError("A abertura das vendas deve ser antes do evento")

    if "ativo" in dados:
        evento.ativo = bool(dados["ativo"])

    db.session.commit()
    return evento


def remover_evento(evento_id: int) -> None:
    evento = buscar_evento(evento_id)
    db.session.delete(evento)
    db.session.commit()
