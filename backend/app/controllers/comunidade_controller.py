import io
from flask import Blueprint, jsonify, request, send_file

from app.extensions import consultar
from app.services import alerta_service, documento_service, grupo_service, recomendacao_service
from app.utils.errors import ServiceError
from app.utils.seguranca import exigir_admin, exigir_login, usuario_atual
from app.utils.vendas import serializar

comunidade_bp = Blueprint('comunidade', __name__)


@comunidade_bp.get('/meia/regras')
def regras():
    return jsonify({'aviso': 'Regras de demonstração acadêmica. Confirme os critérios e documentos com o organizador.',
                    'categorias': documento_service.REGRAS, 'desconto_percentual': 50})


@comunidade_bp.get('/meia/documentos')
@exigir_login
def documentos():
    return jsonify(serializar(documento_service.listar_documentos(usuario_atual())))


@comunidade_bp.post('/meia/documentos')
@exigir_login
def enviar_documento():
    return jsonify(documento_service.enviar_documento(usuario_atual()['id'], request.files.get('arquivo'),
                                                      request.form.get('tipo'), request.form.get('validade'))), 201


@comunidade_bp.get('/meia/documentos/<int:documento_id>/arquivo')
@exigir_login
def baixar_documento(documento_id):
    documento = consultar('SELECT * FROM documentos_meia WHERE id = %s', (documento_id,), apenas_um=True)
    usuario = usuario_atual()
    if not documento or (documento['usuario_id'] != usuario['id'] and usuario['papel'] != 'admin'):
        raise ServiceError('Documento não encontrado.', 404)
    resposta = send_file(io.BytesIO(documento['conteudo']), mimetype=documento['mime'],
                         as_attachment=True, download_name=documento['nome_arquivo'])
    resposta.headers['Cache-Control'] = 'no-store'
    return resposta


@comunidade_bp.put('/meia/documentos/<int:documento_id>')
@exigir_admin
def analisar_documento(documento_id):
    return jsonify(documento_service.analisar_documento(documento_id, request.get_json(silent=True)))


@comunidade_bp.get('/grupos')
@exigir_login
def grupos():
    return jsonify(serializar(grupo_service.listar_grupos(usuario_atual()['id'])))


@comunidade_bp.post('/grupos')
@exigir_login
def criar_grupo():
    return jsonify(serializar(grupo_service.criar_grupo(usuario_atual()['id'], request.get_json(silent=True)))), 201


@comunidade_bp.post('/grupos/entrar')
@exigir_login
def entrar_grupo():
    return jsonify(grupo_service.entrar_grupo(usuario_atual()['id'], request.get_json(silent=True)))


@comunidade_bp.get('/grupos/<int:grupo_id>')
@exigir_login
def detalhar_grupo(grupo_id):
    return jsonify(serializar(grupo_service.detalhar_grupo(usuario_atual()['id'], grupo_id)))


@comunidade_bp.post('/grupos/<int:grupo_id>/sair')
@exigir_login
def sair_grupo(grupo_id):
    return jsonify(grupo_service.sair_grupo(usuario_atual()['id'], grupo_id))


@comunidade_bp.get('/alertas')
@exigir_login
def alertas():
    return jsonify(serializar(alerta_service.listar_alertas(usuario_atual()['id'])))


@comunidade_bp.post('/alertas')
@exigir_login
def agendar_alerta():
    return jsonify(serializar(alerta_service.agendar_alerta(usuario_atual()['id'], request.get_json(silent=True)))), 201


@comunidade_bp.put('/alertas/<int:alerta_id>')
@exigir_login
def alterar_alerta(alerta_id):
    return jsonify(alerta_service.alterar_alerta(usuario_atual()['id'], alerta_id, request.get_json(silent=True)))


@comunidade_bp.get('/recomendacoes')
@exigir_login
def recomendacoes():
    return jsonify(serializar(recomendacao_service.recomendar(usuario_atual()['id'])))
