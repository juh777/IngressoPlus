from datetime import date
from app.repositories import comunidade_repository as repository
from app.utils.errors import ServiceError
from app.utils.vendas import agora

REGRAS = [
    {'tipo': 'estudante', 'titulo': 'Estudante', 'descricao': 'Envie a identificação estudantil com validade na data do evento.'},
    {'tipo': 'idoso', 'titulo': 'Pessoa idosa', 'descricao': 'Envie o documento utilizado para comprovar a categoria.'},
    {'tipo': 'pcd', 'titulo': 'Pessoa com deficiência', 'descricao': 'Envie o comprovante exigido pelo organizador.'},
    {'tipo': 'outro', 'titulo': 'Outras categorias', 'descricao': 'Consulte o organizador sobre os documentos aceitos.'},
]


def enviar_documento(usuario_id, arquivo, tipo, validade):
    if not arquivo or tipo not in [regra['tipo'] for regra in REGRAS]:
        raise ServiceError('Selecione o comprovante e a categoria de meia-entrada.')
    try:
        validade = date.fromisoformat(validade)
    except (TypeError, ValueError):
        raise ServiceError('Validade inválida.')
    if validade < agora().date():
        raise ServiceError('O documento já está vencido.')
    conteudo = arquivo.read(2 * 1024 * 1024 + 1)
    if not conteudo or len(conteudo) > 2 * 1024 * 1024:
        raise ServiceError('Envie um arquivo de até 2 MB.')
    if conteudo.startswith(b'%PDF-'):
        mime = 'application/pdf'
    elif conteudo.startswith(b'\x89PNG\r\n\x1a\n'):
        mime = 'image/png'
    elif conteudo.startswith(b'\xff\xd8\xff'):
        mime = 'image/jpeg'
    else:
        raise ServiceError('Formato não aceito. Use PDF, PNG ou JPG.')
    from werkzeug.utils import secure_filename
    nome = secure_filename(arquivo.filename or 'comprovante')[:150] or 'comprovante'
    documento_id = repository.inserir_documento(usuario_id, tipo, nome, mime, conteudo, validade, agora())
    return {'id': documento_id, 'status': 'pendente', 'mensagem': 'Aguardando análise do administrador.'}


def listar_documentos(usuario):
    return repository.listar_documentos(None if usuario['papel'] == 'admin' else usuario['id'])


def baixar_documento(usuario, documento_id):
    documento = repository.buscar_documento(documento_id)
    if not documento or (documento['usuario_id'] != usuario['id'] and usuario['papel'] != 'admin'):
        raise ServiceError('Documento não encontrado.', 404)
    return documento


def analisar_documento(documento_id, dados):
    from app.utils.validators import exigir_objeto
    exigir_objeto(dados)
    status = dados.get('status')
    observacao = dados.get('observacao', '')
    if status not in ['aprovado', 'rejeitado'] or not isinstance(observacao, str) or len(observacao) > 300:
        raise ServiceError('Informe uma decisão válida e observação de até 300 caracteres.')
    documento = repository.buscar_documento(documento_id)
    if not documento:
        raise ServiceError('Documento não encontrado.', 404)
    if status == 'aprovado' and documento['validade'] < agora().date():
        raise ServiceError('Não é possível aprovar um documento vencido.')
    if status == 'rejeitado' and not observacao.strip():
        raise ServiceError('Explique o motivo da rejeição.')
    repository.atualizar_documento(documento_id, status, observacao.strip())
    return {'status': status}
