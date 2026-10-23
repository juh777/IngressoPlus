"""Dados fictícios opcionais, criados somente pelo comando flask criar-demo."""
from datetime import timedelta
import click
from flask import current_app
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash

from app.extensions import consultar, executar
from app.models.usuario import Usuario
from app.services.eventos import criar_evento
from app.services.lote_service import cadastrar_lote, gerar_assentos
from app.utils.vendas import agora


@click.command('criar-demo')
@with_appcontext
def criar_demo():
    if not current_app.config['MODO_DEMONSTRACAO']:
        raise click.ClickException('Os dados fictícios só podem ser criados em modo demonstração.')
    for nome, email, cpf, papel in [
        ('Administrador Demo', 'admin@ingressoplus.local', '93541134780', 'admin'),
        ('Cliente Demo', 'cliente@ingressoplus.local', '11144477735', 'cliente'),
    ]:
        usuario = Usuario.buscar_por_email(email)
        if not usuario:
            usuario = Usuario(nome=nome, email=email, cpf=cpf, senha_hash=generate_password_hash('DemoIngresso123!')).salvar()
            executar('UPDATE usuarios SET papel = %s WHERE id = %s', (papel, usuario.id))
    for indice, categoria in enumerate(['Música', 'Teatro', 'Tecnologia']):
        nome = 'Demonstração - ' + categoria
        existente = consultar('SELECT id FROM eventos WHERE nome = %s', (nome,), apenas_um=True)
        if existente:
            continue
        data = agora() + timedelta(days=45 + indice)
        evento = criar_evento({'nome': nome, 'local': 'Espaço Ingresso+', 'categoria': categoria,
                              'descricao': 'Evento fictício para testar o fluxo completo, sem cobrança real.',
                              'data_hora_evento': data.isoformat(),
                              'data_abertura_vendas': (agora() - timedelta(days=1)).isoformat()})
        cadastrar_lote(evento.id, {'nome': 'Lote de demonstração', 'preco': '100.00', 'quantidade': 30,
                                 'taxa_percentual': 10, 'inicio': (agora() - timedelta(days=1)).isoformat(),
                                 'fim': (data - timedelta(hours=1)).isoformat()})
        if indice == 0:
            gerar_assentos(evento.id, {'setor': 'Plateia', 'filas': 3, 'por_fila': 10})
    click.echo('Demonstração pronta. Contas admin@ingressoplus.local e cliente@ingressoplus.local; senha DemoIngresso123!')


def configurar_demo(app):
    app.cli.add_command(criar_demo)
