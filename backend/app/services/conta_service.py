import base64
import hashlib
import json

from cryptography.fernet import Fernet, InvalidToken
from flask import current_app, session
from werkzeug.security import check_password_hash

from app.extensions import consultar, executar
from app.models.usuario import Usuario
from app.services.usuarios import criar_usuario, atualizar_usuario
from app.utils.errors import ServiceError
from app.utils.validators import exigir_objeto
from app.utils.vendas import agora


def registrar_acao(usuario_id, acao):
    executar('INSERT INTO auditoria (usuario_id, acao, criado_em) VALUES (%s, %s, %s)',
             (usuario_id, acao, agora()))


def entrar(dados):
    dados = exigir_objeto(dados)
    email = dados.get('email', '')
    senha = dados.get('senha', '')
    if not isinstance(email, str) or not isinstance(senha, str):
        raise ServiceError('E-mail ou senha inválidos.', 401)
    usuario = Usuario.buscar_por_email(email.strip().lower())
    if not usuario or not usuario.ativo or not check_password_hash(usuario.senha_hash, senha):
        raise ServiceError('E-mail ou senha inválidos.', 401)
    session.clear()
    session['usuario_id'] = usuario.id
    session.permanent = True
    registrar_acao(usuario.id, 'Login na conta')
    return usuario.to_dict()


def cadastrar(dados):
    usuario = criar_usuario(dados)
    session.clear()
    session['usuario_id'] = usuario.id
    registrar_acao(usuario.id, 'Cadastro da conta')
    return usuario.to_dict()


def atualizar_perfil(usuario_id, dados):
    dados = exigir_objeto(dados)
    permitidos = ['nome', 'email', 'cpf', 'telefone', 'senha']
    dados = {chave: valor for chave, valor in dados.items() if chave in permitidos}
    usuario = atualizar_usuario(usuario_id, dados)
    registrar_acao(usuario_id, 'Atualização do perfil')
    return usuario.to_dict()


def chave_cofre():
    chave = current_app.config['COFRE_SECRET_KEY']
    if not chave:
        # A chave de sessão deve ser aleatória e persistente no .env.
        chave = base64.urlsafe_b64encode(hashlib.sha256(current_app.config['SECRET_KEY'].encode()).digest())
    return Fernet(chave)


def ler_cofre(usuario_id):
    linha = consultar('SELECT conteudo FROM cofre_dados WHERE usuario_id = %s', (usuario_id,), apenas_um=True)
    if not linha:
        return {'consentimento': False, 'endereco': '', 'cidade': '', 'preferencias': ''}
    try:
        return json.loads(chave_cofre().decrypt(linha['conteudo'].encode()).decode())
    except InvalidToken:
        raise ServiceError('A chave do cofre foi alterada. Restaure a chave original do ambiente.', 503)


def salvar_cofre(usuario_id, dados):
    dados = exigir_objeto(dados)
    if dados.get('consentimento') is not True:
        executar('DELETE FROM cofre_dados WHERE usuario_id = %s', (usuario_id,))
        registrar_acao(usuario_id, 'Consentimento do cofre revogado e dados removidos')
        return ler_cofre(usuario_id)
    conteudo = {'consentimento': True}
    for campo in ['endereco', 'cidade', 'preferencias']:
        valor = dados.get(campo, '')
        if not isinstance(valor, str) or len(valor) > 300:
            raise ServiceError(f'{campo} deve ter até 300 caracteres.')
        conteudo[campo] = valor.strip()
    criptografado = chave_cofre().encrypt(json.dumps(conteudo, ensure_ascii=False).encode()).decode()
    executar('''INSERT INTO cofre_dados (usuario_id, conteudo, atualizado_em) VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE conteudo = VALUES(conteudo), atualizado_em = VALUES(atualizado_em)''',
             (usuario_id, criptografado, agora()))
    registrar_acao(usuario_id, 'Dados salvos no cofre com consentimento')
    return conteudo


def exportar_dados(usuario_id):
    registrar_acao(usuario_id, 'Exportação dos próprios dados')
    return {
        'perfil': Usuario.buscar_por_id(usuario_id).to_dict(),
        'cofre': ler_cofre(usuario_id),
        'reservas': consultar('SELECT * FROM reservas WHERE usuario_id = %s', (usuario_id,)),
        'ingressos': consultar('SELECT * FROM ingressos WHERE usuario_id = %s', (usuario_id,)),
        'pagamentos': consultar('''SELECT p.* FROM pagamentos p JOIN reservas r ON r.id = p.reserva_id
                                  WHERE r.usuario_id = %s''', (usuario_id,)),
        'documentos': consultar('''SELECT id, tipo, nome_arquivo, validade, status, observacao
                                  FROM documentos_meia WHERE usuario_id = %s''', (usuario_id,)),
        'alertas': consultar('SELECT * FROM alertas WHERE usuario_id = %s', (usuario_id,)),
        'grupos': consultar('''SELECT g.id, g.nome, g.evento_id FROM grupos g JOIN grupo_membros m
                              ON m.grupo_id = g.id WHERE m.usuario_id = %s''', (usuario_id,)),
        'historico': consultar('SELECT acao, criado_em FROM auditoria WHERE usuario_id = %s ORDER BY id DESC',
                              (usuario_id,)),
    }
