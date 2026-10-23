from app.extensions import consultar, executar, transacao
from app.repositories import vendas_repository as repository
from app.services.eventos.helpers import data_hora_iso
from app.utils.errors import ServiceError
from app.utils.validators import exigir_objeto
from app.utils.vendas import agora, dinheiro, inteiro, texto


def evento_existente(evento_id):
    evento = repository.buscar_evento(evento_id)
    if not evento:
        raise ServiceError('Evento não encontrado.', 404)
    return evento


def consultar_lotes(evento_id):
    evento = evento_existente(evento_id)
    lotes = repository.listar_lotes(evento_id)
    for lote in lotes:
        lote['disponiveis'] = max(0, lote['quantidade'] - int(lote['ocupados']))
        lote['aberto'] = bool(evento['ativo'] and lote['ativo'] and lote['inicio'] <= agora() <= lote['fim']
                              and evento['data_hora_evento'] > agora())
    return lotes


def cadastrar_lote(evento_id, dados):
    dados = exigir_objeto(dados)
    evento = evento_existente(evento_id)
    inicio = data_hora_iso(dados.get('inicio'), 'inicio')
    fim = data_hora_iso(dados.get('fim'), 'fim')
    if inicio >= fim or fim > evento['data_hora_evento']:
        raise ServiceError('O início deve ser anterior ao fim e as vendas devem terminar até o evento.')
    lote_id = executar('''INSERT INTO lotes (evento_id, nome, preco, quantidade, taxa_percentual, inicio, fim)
                         VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                        (evento_id, texto(dados, 'nome'), dinheiro(dados.get('preco'), 'Preço', '0.01'),
                         inteiro(dados.get('quantidade'), 'Quantidade'),
                         dinheiro(dados.get('taxa_percentual', 10), 'Taxa', '0', '50'), inicio, fim))
    return consultar('SELECT * FROM lotes WHERE id = %s', (lote_id,), apenas_um=True)


def gerar_assentos(evento_id, dados):
    exigir_objeto(dados)
    evento_existente(evento_id)
    filas = inteiro(dados.get('filas'), 'Filas', 1, 10)
    por_fila = inteiro(dados.get('por_fila'), 'Assentos por fila', 1, 20)
    setor = texto(dados, 'setor', 80)
    with transacao() as cursor:
        cursor.execute('SELECT id FROM eventos WHERE id = %s FOR UPDATE', (evento_id,))
        cursor.execute('SELECT id FROM reservas WHERE evento_id = %s LIMIT 1', (evento_id,))
        if cursor.fetchone():
            raise ServiceError('O mapa só pode ser criado antes da primeira reserva.', 409)
        cursor.execute('SELECT id FROM assentos WHERE evento_id = %s LIMIT 1', (evento_id,))
        if cursor.fetchone():
            raise ServiceError('Este evento já possui um mapa. Os assentos existentes foram mantidos.', 409)
        for fila in range(filas):
            for numero in range(1, por_fila + 1):
                cursor.execute('INSERT INTO assentos (evento_id, setor, fila, numero) VALUES (%s, %s, %s, %s)',
                               (evento_id, setor, chr(65 + fila), numero))
    return repository.mapa_assentos(evento_id)


def comparar_taxas(lote_id, quantidade, tipo):
    lote = consultar('SELECT * FROM lotes WHERE id = %s', (lote_id,), apenas_um=True)
    if not lote:
        raise ServiceError('Lote não encontrado.', 404)
    quantidade = inteiro(quantidade, 'Quantidade', 1, 10)
    if tipo not in ['inteira', 'meia']:
        raise ServiceError('Tipo de ingresso inválido.')
    preco = lote['preco'] if tipo == 'inteira' else dinheiro(lote['preco'] / 2)
    subtotal = preco * quantidade
    canais = [('Ingresso+', lote['taxa_percentual'], dinheiro(0)),
              ('Canal A (simulado)', dinheiro(15), dinheiro(2)),
              ('Canal B (simulado)', dinheiro(8), dinheiro(5))]
    resultado = []
    for nome, percentual, fixa in canais:
        taxa = dinheiro(subtotal * percentual / 100 + fixa)
        resultado.append({'canal': nome, 'subtotal': subtotal, 'taxa': taxa, 'total': subtotal + taxa})
    return sorted(resultado, key=lambda item: item['total'])
