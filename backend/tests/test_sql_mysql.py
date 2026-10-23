"""Casos importantes para a troca do ORM por SQL direto."""
from datetime import datetime

from pymysql import IntegrityError
from werkzeug.security import check_password_hash

from test_api import ApiTestCase
from app.extensions import consultar
from app.models.usuario import Usuario


class SqlMySQLTest(ApiTestCase):
    def test_busca_nao_executa_sql_recebido_no_formulario(self):
        self.criar_usuario()
        resposta = self.client.get('/api/usuarios/busca', query_string={'termo': "' OR 1=1 -- "})
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.get_json(), [])
        self.assertEqual(len(self.client.get('/api/usuarios').get_json()), 2)

    def test_filtro_nao_executa_sql_recebido_no_formulario(self):
        self.criar_evento()
        resposta = self.client.get('/api/eventos/filtro', query_string={'local': "'; DROP TABLE eventos; --"})
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.get_json(), [])
        self.assertEqual(len(self.client.get('/api/eventos').get_json()), 1)

    def test_texto_com_apostrofo_e_acentos(self):
        evento = self.criar_evento(nome="Show d'Água", local="Teatro São João")
        resposta = self.client.get('/api/eventos/filtro', query_string={'local': 'SÃO JOÃO'})
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.get_json()[0]['nome'], evento['nome'])

    def test_senha_continua_com_hash_e_edicao_mantem_senha(self):
        usuario = self.criar_usuario()
        antes = consultar('SELECT senha_hash FROM usuarios WHERE id = %s', (usuario['id'],), apenas_um=True)
        self.assertTrue(check_password_hash(antes['senha_hash'], 'senha-segura'))
        resposta = self.client.put(f"/api/usuarios/{usuario['id']}", json={'nome': 'Nome Editado'})
        self.assertEqual(resposta.status_code, 200)
        depois = consultar('SELECT senha_hash FROM usuarios WHERE id = %s', (usuario['id'],), apenas_um=True)
        self.assertEqual(antes, depois)
        self.assertNotIn('senha_hash', resposta.get_json())

    def test_rollback_permite_nova_gravacao_apos_duplicidade(self):
        usuario = self.criar_usuario()
        duplicado = Usuario(nome='Duplicado', email=usuario['email'], cpf='11144477735', senha_hash='teste')
        with self.assertRaises(IntegrityError):
            duplicado.salvar()
        self.criar_usuario(nome='Bruno', email='bruno@example.com', cpf='11144477735')
        self.assertEqual(len(self.client.get('/api/usuarios').get_json()), 3)

    def test_datas_com_fuso_sao_normalizadas_para_utc(self):
        evento = self.criar_evento(data_hora_evento='2026-12-15T20:00:00-03:00')
        resposta = self.client.get(f"/api/eventos/{evento['id']}")
        self.assertEqual(resposta.get_json()['data_hora_evento'], '2026-12-15T23:00:00')
        datetime.fromisoformat(resposta.get_json()['criado_em'])

    def test_corpo_json_invalido_retorna_erro_de_validacao(self):
        for corpo in [None, [], 'texto', 123]:
            resposta = self.client.post('/api/usuarios', json=corpo)
            self.assertEqual(resposta.status_code, 400)
            self.assertIn('erro', resposta.get_json())

    def test_status_invalido_e_booleano_false(self):
        evento = self.criar_evento()
        resposta = self.client.put(f"/api/eventos/{evento['id']}", json={'ativo': 'false'})
        self.assertEqual(resposta.status_code, 200)
        self.assertIs(resposta.get_json()['ativo'], False)
        self.assertEqual(self.client.get('/api/eventos/filtro?status=invalido').status_code, 400)
