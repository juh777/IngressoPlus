"""Importa o JSON exportado do PostgreSQL para um MySQL vazio."""
import json
import sys
from datetime import datetime
from pathlib import Path

# Permite executar o arquivo a partir da raiz do backend.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app
from app.extensions import obter_conexao


def importar(caminho):
    dados = json.loads(Path(caminho).read_text(encoding='utf-8-sig'))
    campos_por_tabela = {
        'usuarios': ['id', 'nome', 'email', 'cpf', 'telefone', 'senha_hash',
                     'ativo', 'criado_em', 'atualizado_em'],
        'eventos': ['id', 'nome', 'descricao', 'local', 'categoria', 'imagem_url',
                    'data_hora_evento', 'data_abertura_vendas', 'ativo',
                    'criado_em', 'atualizado_em'],
    }
    campos_data = ['criado_em', 'atualizado_em', 'data_hora_evento', 'data_abertura_vendas']

    with create_app().app_context():
        conexao = obter_conexao()
        try:
            with conexao.cursor() as cursor:
                # Os nomes das tabelas e colunas vêm das listas fixas acima.
                for tabela in campos_por_tabela:
                    cursor.execute(f'SELECT COUNT(*) AS total FROM `{tabela}`')
                    if cursor.fetchone()['total']:
                        raise ValueError('O MySQL precisa estar vazio para importar os dados.')

                for tabela, campos in campos_por_tabela.items():
                    colunas = ', '.join('`' + campo + '`' for campo in campos)
                    marcadores = ', '.join(['%s'] * len(campos))
                    for registro in dados[tabela]:
                        for campo in campos_data:
                            if campo in registro:
                                registro[campo] = datetime.fromisoformat(registro[campo])
                        valores = [registro[campo] for campo in campos]
                        cursor.execute(f'INSERT INTO `{tabela}` ({colunas}) VALUES ({marcadores})', valores)

                    # Compara todos os campos, incluindo IDs, datas e hashes.
                    cursor.execute(f'SELECT {colunas} FROM `{tabela}` ORDER BY id')
                    if cursor.fetchall() != dados[tabela]:
                        raise ValueError(f'Os dados da tabela {tabela} não conferem com o backup.')

            conexao.commit()
        except Exception:
            conexao.rollback()
            raise

    for tabela in campos_por_tabela:
        print(f'{tabela}: {len(dados[tabela])} registros importados e conferidos.')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Uso: python migrations/importar_postgres.py caminho/dados.json')
    importar(sys.argv[1])
