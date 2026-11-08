import secrets
from app.extensions import transacao
from app.repositories import comunidade_repository as repository
from app.services.lote_service import evento_existente
from app.utils.errors import ServiceError
from app.utils.validators import exigir_objeto
from app.utils.vendas import agora, inteiro, texto


def listar_grupos(usuario_id):
    return repository.listar_grupos(usuario_id)


def criar_grupo(usuario_id, dados):
    exigir_objeto(dados)
    evento_id = inteiro(dados.get('evento_id'), 'Evento')
    evento_existente(evento_id)
    with transacao() as cursor:
        grupo_id = repository.inserir_grupo(cursor, evento_id, usuario_id, texto(dados, 'nome'),
                                           secrets.token_hex(5).upper(), agora())
    return detalhar_grupo(usuario_id, grupo_id)


def entrar_grupo(usuario_id, dados):
    exigir_objeto(dados)
    codigo = texto(dados, 'codigo', 24).upper()
    with transacao() as cursor:
        grupo = repository.bloquear_grupo_por_codigo(cursor, codigo)
        if not grupo:
            raise ServiceError('Código de grupo não encontrado.', 404)
        membros = repository.listar_membros(cursor, grupo['id'])
        if any(membro['usuario_id'] == usuario_id for membro in membros):
            return {'id': grupo['id'], 'mensagem': 'Você já participa deste grupo.'}
        if len(membros) >= 20:
            raise ServiceError('Este grupo atingiu o limite de 20 participantes.', 409)
        repository.inserir_membro(cursor, grupo['id'], usuario_id)
    return {'id': grupo['id'], 'mensagem': 'Participação confirmada.'}


def detalhar_grupo(usuario_id, grupo_id):
    grupo = repository.buscar_grupo_do_membro(usuario_id, grupo_id)
    if not grupo:
        raise ServiceError('Grupo não encontrado.', 404)
    grupo['membros'] = repository.resumo_membros(grupo['evento_id'], grupo_id)
    for membro in grupo['membros']:
        membro['ingressos'] = int(membro['ingressos'])
    return grupo


def sair_grupo(usuario_id, grupo_id):
    with transacao() as cursor:
        grupo = repository.bloquear_grupo(cursor, grupo_id)
        if not grupo:
            raise ServiceError('Grupo não encontrado.', 404)
        if grupo['criador_id'] == usuario_id:
            raise ServiceError('O criador deve permanecer no grupo para manter a organização.', 409)
        repository.remover_membro(cursor, grupo_id, usuario_id)
    return {'mensagem': 'Você saiu do grupo.'}
