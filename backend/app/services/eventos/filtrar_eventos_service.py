from app.repositories.evento_repository import EventoRepository
from app.utils.errors import ServiceError


def filtrar_eventos(
    categoria: str | None = None,
    local: str | None = None,
    status: str | None = None,
):
    categoria_normalizada = categoria.strip() if isinstance(categoria, str) else None
    local_normalizado = local.strip() if isinstance(local, str) else None
    status_normalizado = status.strip().lower() if isinstance(status, str) else ""

    if status_normalizado not in {"", "ativo", "inativo"}:
        raise ServiceError("Parametro 'status' deve ser 'ativo' ou 'inativo'")

    ativo = {"ativo": True, "inativo": False}.get(status_normalizado)
    return EventoRepository.filtrar(
        categoria=categoria_normalizada or None,
        local=local_normalizado or None,
        status=ativo,
    )
