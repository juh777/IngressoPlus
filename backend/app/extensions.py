"""Conexão MySQL compartilhada durante cada requisição Flask."""
from pathlib import Path
from contextlib import contextmanager

import click
import pymysql
from flask import current_app, g
from flask.cli import with_appcontext
from flask_cors import CORS
from pymysql.cursors import DictCursor

cors = CORS()

def conectar_banco():
    return pymysql.connect(
        host=current_app.config['DB_HOST'],
        port=current_app.config['DB_PORT'],
        user=current_app.config['DB_USER'],
        password=current_app.config['DB_PASSWORD'],
        database=current_app.config['DB_NAME'],
        charset='utf8mb4',
        cursorclass=DictCursor,
        connect_timeout=10,
        init_command='SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED',
    )

def obter_conexao():
    # g guarda uma conexão por requisição. Não abrimos uma a cada consulta.
    if 'conexao' not in g:
        g.conexao = conectar_banco()
    return g.conexao

def fechar_conexao(erro=None):
    conexao = g.pop('conexao', None)
    if conexao is not None:
        conexao.close()

def consultar(sql, parametros=(), apenas_um=False):
    with obter_conexao().cursor() as cursor:
        cursor.execute(sql, parametros)
        if apenas_um:
            return cursor.fetchone()
        return cursor.fetchall()

def executar(sql, parametros=()):
    conexao = obter_conexao()
    try:
        with conexao.cursor() as cursor:
            cursor.execute(sql, parametros)
            novo_id = cursor.lastrowid
        conexao.commit()
        return novo_id
    except pymysql.MySQLError:
        conexao.rollback()
        raise

@contextmanager
def transacao():
    """Agrupa reserva, pagamento e ingressos: confirma tudo ou desfaz tudo."""
    conexao = obter_conexao()
    conexao.begin()
    try:
        with conexao.cursor() as cursor:
            yield cursor
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise

def criar_tabelas():
    pasta = Path(current_app.root_path).parent / 'migrations/versions'
    for nome in ['001_tabelas_iniciais.sql', '002_vendas.sql']:
        for comando in (pasta / nome).read_text(encoding='utf-8').split(';'):
            if comando.strip():
                executar(comando)
    coluna = consultar("SHOW COLUMNS FROM usuarios LIKE 'papel'", apenas_um=True)
    if not coluna:
        executar("ALTER TABLE usuarios ADD COLUMN papel VARCHAR(20) NOT NULL DEFAULT 'cliente'")
        # Preserva o usuário anterior como administrador na primeira atualização.
        executar("UPDATE usuarios SET papel = 'admin' ORDER BY id LIMIT 1")
    procedimento = consultar(
        'SELECT ROUTINE_NAME FROM information_schema.ROUTINES WHERE ROUTINE_SCHEMA = DATABASE() AND ROUTINE_NAME = %s',
        ('obter_mapa_assentos',), apenas_um=True,
    )
    if not procedimento:
        executar((pasta / '003_mapa.sql').read_text(encoding='utf-8'))

@click.command('init-db')
@with_appcontext
def iniciar_banco():
    """Cria as tabelas que ainda não existem, sem apagar registros."""
    criar_tabelas()
    click.echo('Tabelas do MySQL prontas.')

def configurar_banco(app):
    app.teardown_appcontext(fechar_conexao)
    app.cli.add_command(iniciar_banco)
