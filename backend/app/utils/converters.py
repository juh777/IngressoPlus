from app.utils.errors import ServiceError


def normalizar_booleano(valor: object, campo: str = "ativo") -> bool:
    """Converte valores JSON usuais para booleano sem aceitar ambiguidade."""
    if isinstance(valor, bool):
        return valor
    if isinstance(valor, str):
        valor_normalizado = valor.strip().lower()
        if valor_normalizado in {"true", "1", "sim", "ativo"}:
            return True
        if valor_normalizado in {"false", "0", "nao", "não", "inativo"}:
            return False
    if isinstance(valor, int) and valor in {0, 1}:
        return bool(valor)
    raise ServiceError(f"Campo '{campo}' deve ser verdadeiro ou falso")
