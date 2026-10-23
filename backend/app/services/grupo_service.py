import secrets
from app.extensions import consultar, transacao
from app.services.lote_service import evento_existente
from app.utils.errors import ServiceError
from app.utils.validators import exigir_objeto
from app.utils.vendas import agora, inteiro, texto


def listar_grupos(usuario_id):
    return consultar('''SELECT g.*, e.nome AS evento FROM grupos g JOIN eventos e ON e.id = g.evento_id
                        JOIN grupo_membros m ON m.grupo_id = g.id WHERE m.usuario_id = %s ORDER BY g.id DESC''', (usuario_id,))


def criar_grupo(usuario_id, dados):
    exigir_objeto(dados)
    evento_id = inteiro(dados.get('evento_id'), 'Evento')
    evento_existente(evento_id)
    with transacao() as cursor:
        cursor.execute('INSERT INTO grupos (evento_id, criador_id, nome, codigo, criado_em) VALUES (%s,%s,%s,%s,%s)',
                       (evento_id, usuario_id, texto(dados, 'nome'), secrets.token_hex(5).upper(), agora()))
        grupo_id = cursor.lastrowid
        cursor.execute('INSERT INTO grupo_membros (grupo_id, usuario_id) VALUES (%s,%s)', (grupo_id, usuario_id))
    return detalhar_grupo(usuario_id, grupo_id)


def entrar_grupo(usuario_id, dados):
    exigir_objeto(dados)
    codigo = texto(dados, 'codigo', 24).upper()
    with transacao() as cursor:
        cursor.execute('SELECT * FROM grupos WHERE codigo = %s FOR UPDATE', (codigo,))
        grupo = cursor.fetchone()
        if not grupo:
            raise ServiceError('Código de grupo não encontrado.', 404)
        cursor.execute('SELECT usuario_id FROM grupo_membros WHERE grupo_id = %s', (grupo['id'],))
        membros = cursor.fetchall()
        if any(membro['usuario_id'] == usuario_id for membro in membros):
            return {'id': grupo['id'], 'mensagem': 'Você já participa deste grupo.'}
        if len(membros) >= 20:
            raise ServiceError('Este grupo atingiu o limite de 20 participantes.', 409)
        cursor.execute('INSERT INTO grupo_membros (grupo_id, usuario_id) VALUES (%s,%s)', (grupo['id'], usuario_id))
    return {'id': grupo['id'], 'mensagem': 'Participação confirmada.'}


def detalhar_grupo(usuario_id, grupo_id):
    grupo = consultar('''SELECT g.*, e.nome AS evento FROM grupos g JOIN eventos e ON e.id = g.evento_id
                        JOIN grupo_membros m ON m.grupo_id = g.id
                        WHERE g.id = %s AND m.usuario_id = %s''', (grupo_id, usuario_id), apenas_um=True)
    if not grupo:
        raise ServiceError('Grupo não encontrado.', 404)
    grupo['membros'] = consultar('''SELECT u.id, u.nome,
        COALESCE(SUM(CASE WHEN r.status = 'paga' THEN r.total ELSE 0 END), 0) AS total_pago,
        COALESCE(SUM(CASE WHEN r.status = 'paga' THEN r.quantidade ELSE 0 END), 0) AS ingressos
        FROM grupo_membros m JOIN usuarios u ON u.id = m.usuario_id
        LEFT JOIN reservas r ON r.usuario_id = u.id AND r.evento_id = %s
        WHERE m.grupo_id = %s GROUP BY u.id ORDER BY u.nome''', (grupo['evento_id'], grupo_id))
    for membro in grupo['membros']:
        membro['ingressos'] = int(membro['ingressos'])
    return grupo


def sair_grupo(usuario_id, grupo_id):
    with transacao() as cursor:
        cursor.execute('SELECT * FROM grupos WHERE id = %s FOR UPDATE', (grupo_id,))
        grupo = cursor.fetchone()
        if not grupo:
            raise ServiceError('Grupo não encontrado.', 404)
        if grupo['criador_id'] == usuario_id:
            raise ServiceError('O criador deve permanecer no grupo para manter a organização.', 409)
        cursor.execute('DELETE FROM grupo_membros WHERE grupo_id = %s AND usuario_id = %s', (grupo_id, usuario_id))
    return {'mensagem': 'Você saiu do grupo.'}
