from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from app.utils.errors import ServiceError


def agora():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def inteiro(valor, campo, minimo=1, maximo=10000):
    # Não aceita decimais, booleanos nem conversões silenciosas como int(1.5).
    if isinstance(valor, bool) or not str(valor).isdigit():
        raise ServiceError(f'{campo} deve ser um número inteiro.')
    numero = int(valor)
    if not minimo <= numero <= maximo:
        raise ServiceError(f'{campo} deve estar entre {minimo} e {maximo}.')
    return numero


def dinheiro(valor, campo='Valor', minimo='0', maximo='999999.99'):
    try:
        numero = Decimal(str(valor))
        if not numero.is_finite() or numero < Decimal(minimo) or numero > Decimal(maximo):
            raise ValueError()
        return numero.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError, TypeError):
        raise ServiceError(f'{campo} inválido.')


def texto(dados, campo, limite=100):
    valor = dados.get(campo)
    if not isinstance(valor, str) or not valor.strip() or len(valor.strip()) > limite:
        raise ServiceError(f'{campo}: informe um texto de até {limite} caracteres.')
    return valor.strip()


def serializar(valor):
    # A API envia datas ISO e dinheiro como texto, sem perder centavos.
    if isinstance(valor, dict):
        return {chave: serializar(item) for chave, item in valor.items()}
    if isinstance(valor, (list, tuple)):
        return [serializar(item) for item in valor]
    if isinstance(valor, Decimal):
        return format(valor, '.2f')
    if hasattr(valor, 'isoformat'):
        return valor.isoformat()
    return valor
