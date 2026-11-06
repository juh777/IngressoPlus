"""Regressões de tamanho: HTTP 400 antes de salvar e limites reais do MySQL."""
from unittest.mock import patch

from test_api import ApiTestCase
from app.extensions import consultar


USUARIO = {
    'nome': 'Cliente dos limites', 'email': 'limites@example.com',
    'cpf': '52998224725', 'telefone': '11999990000', 'senha': 'senha-limites',
}
EVENTO = {
    'nome': 'Evento dos limites', 'local': 'Teatro',
    'data_hora_evento': '2026-12-15T20:00:00',
    'data_abertura_vendas': '2026-10-01T09:00:00',
}
LIMITES_USUARIO = {'nome': 150, 'email': 150, 'telefone': 20}
LIMITES_EVENTO = {'nome': 150, 'local': 200, 'categoria': 80, 'imagem_url': 300}


class LimitesTextoTest(ApiTestCase):
    def campos_usuario_excedidos(self):
        return [(campo, 'x' * (limite + 1) if campo != 'email'
                 else 'a' * (limite + 1 - len('@example.com')) + '@example.com', limite)
                for campo, limite in LIMITES_USUARIO.items()]

    def campos_evento_excedidos(self):
        return [(campo, 'x' * (limite + 1), limite)
                for campo, limite in LIMITES_EVENTO.items()] + [
                    ('descricao', 'a' * 65536, 65535),
                    ('descricao', 'á' * 32768, 65535),
                ]

    def conferir_erro(self, resposta, campo, limite):
        self.assertEqual(resposta.status_code, 400, resposta.get_json())
        mensagem = resposta.get_json()['erro']
        self.assertIn(campo, mensagem)
        self.assertIn(str(limite), mensagem)
        self.assertIn('bytes em UTF-8' if campo == 'descricao' else 'caracteres', mensagem)

    def test_criacao_usuario_rejeita_excesso_antes_de_salvar(self):
        antes = consultar('SELECT * FROM usuarios ORDER BY id')
        for campo, valor, limite in self.campos_usuario_excedidos():
            with self.subTest(campo=campo), patch(
                'app.repositories.usuario_repository.UsuarioRepository.salvar'
            ) as salvar:
                resposta = self.client.post('/api/usuarios', json={**USUARIO, campo: valor})
                self.conferir_erro(resposta, campo, limite)
                salvar.assert_not_called()
                self.assertEqual(consultar('SELECT * FROM usuarios ORDER BY id'), antes)
        self.criar_usuario(**USUARIO)

    def test_edicao_usuario_rejeita_excesso_sem_alterar_dados(self):
        usuario = self.criar_usuario(**USUARIO)
        antes = consultar('SELECT * FROM usuarios ORDER BY id')
        for campo, valor, limite in self.campos_usuario_excedidos():
            with self.subTest(campo=campo), patch(
                'app.repositories.usuario_repository.UsuarioRepository.salvar'
            ) as salvar:
                resposta = self.client.put(f"/api/usuarios/{usuario['id']}", json={campo: valor})
                self.conferir_erro(resposta, campo, limite)
                salvar.assert_not_called()
                self.assertEqual(consultar('SELECT * FROM usuarios ORDER BY id'), antes)
        resposta = self.client.put(f"/api/usuarios/{usuario['id']}", json={'nome': 'Nome válido'})
        self.assertEqual(resposta.status_code, 200, resposta.get_json())

    def test_cadastro_publico_rejeita_campos_excedidos(self):
        cliente = self.app.test_client()
        antes = consultar('SELECT * FROM usuarios ORDER BY id')
        for campo, valor, limite in self.campos_usuario_excedidos():
            with self.subTest(campo=campo):
                resposta = cliente.post('/api/auth/cadastro', json={**USUARIO, campo: valor})
                self.conferir_erro(resposta, campo, limite)
                self.assertEqual(consultar('SELECT * FROM usuarios ORDER BY id'), antes)
                self.assertEqual(cliente.get('/api/auth/sessao').status_code, 401)
        self.assertEqual(cliente.post('/api/auth/cadastro', json=USUARIO).status_code, 201)

    def test_perfil_rejeita_campos_excedidos_sem_alterar_dados(self):
        cliente = self.app.test_client()
        self.assertEqual(cliente.post('/api/auth/cadastro', json=USUARIO).status_code, 201)
        antes = consultar('SELECT * FROM usuarios ORDER BY id')
        for campo, valor, limite in self.campos_usuario_excedidos():
            with self.subTest(campo=campo):
                resposta = cliente.put('/api/perfil', json={campo: valor})
                self.conferir_erro(resposta, campo, limite)
                self.assertEqual(consultar('SELECT * FROM usuarios ORDER BY id'), antes)
        resposta = cliente.put('/api/perfil', json={'nome': 'Perfil válido'})
        self.assertEqual(resposta.status_code, 200, resposta.get_json())
        self.assertEqual(resposta.get_json()['papel'], 'cliente')

    def test_criacao_evento_rejeita_excesso_antes_de_salvar(self):
        for campo, valor, limite in self.campos_evento_excedidos():
            with self.subTest(campo=campo, bytes=len(valor.encode('utf-8'))), patch(
                'app.repositories.evento_repository.EventoRepository.salvar'
            ) as salvar:
                resposta = self.client.post('/api/eventos', json={**EVENTO, campo: valor})
                self.conferir_erro(resposta, campo, limite)
                salvar.assert_not_called()
                self.assertEqual(consultar('SELECT COUNT(*) AS total FROM eventos')[0]['total'], 0)
        self.criar_evento(**EVENTO)

    def test_edicao_evento_rejeita_excesso_sem_alterar_dados(self):
        evento = self.criar_evento(**EVENTO)
        antes = consultar('SELECT * FROM eventos')
        for campo, valor, limite in self.campos_evento_excedidos():
            with self.subTest(campo=campo, bytes=len(valor.encode('utf-8'))), patch(
                'app.repositories.evento_repository.EventoRepository.salvar'
            ) as salvar:
                resposta = self.client.put(f"/api/eventos/{evento['id']}", json={campo: valor})
                self.conferir_erro(resposta, campo, limite)
                salvar.assert_not_called()
                self.assertEqual(consultar('SELECT * FROM eventos'), antes)
        resposta = self.client.put(f"/api/eventos/{evento['id']}", json={'nome': 'Evento válido'})
        self.assertEqual(resposta.status_code, 200, resposta.get_json())

    def test_usuario_aceita_limites_exatos_apos_normalizacao(self):
        email = 'a' * (150 - len('@example.com')) + '@example.com'
        dados = {'nome': 'Á' * 149 + '😀', 'email': email, 'telefone': '1' * 20}
        usuario = self.criar_usuario(**{**USUARIO, **dados, 'nome': ' ' + dados['nome'] + ' ',
                                       'email': ' ' + email.upper() + ' '})
        for campo, valor in dados.items():
            self.assertEqual(usuario[campo], valor)
        dados['nome'] = '界' * 150
        dados['telefone'] = '2' * 20
        resposta = self.client.put(f"/api/usuarios/{usuario['id']}", json=dados)
        self.assertEqual(resposta.status_code, 200, resposta.get_json())
        banco = consultar('SELECT * FROM usuarios WHERE id = %s', (usuario['id'],), apenas_um=True)
        for campo, valor in dados.items():
            self.assertEqual(banco[campo], valor)

    def test_evento_aceita_limites_exatos_inclusive_text_em_bytes(self):
        dados = {campo: '界' * limite for campo, limite in LIMITES_EVENTO.items()}
        dados['descricao'] = 'á' * 32767 + 'a'
        evento = self.criar_evento(**{**EVENTO, **dados})
        for campo, valor in dados.items():
            self.assertEqual(evento[campo], valor)
        dados['descricao'] = '😀' * 16383 + 'áa'
        resposta = self.client.put(f"/api/eventos/{evento['id']}", json=dados)
        self.assertEqual(resposta.status_code, 200, resposta.get_json())
        banco = consultar('SELECT * FROM eventos WHERE id = %s', (evento['id'],), apenas_um=True)
        for campo, valor in dados.items():
            self.assertEqual(banco[campo], valor)
        self.assertEqual(len(banco['descricao'].encode('utf-8')), 65535)

    def test_opcionais_continuam_aceitando_nulo_e_vazio(self):
        usuario = self.criar_usuario(**USUARIO)
        evento = self.criar_evento(**EVENTO)
        for vazio in [None, '', '   ']:
            with self.subTest(valor=vazio):
                resposta = self.client.put(f"/api/usuarios/{usuario['id']}", json={'telefone': vazio})
                self.assertEqual(resposta.status_code, 200, resposta.get_json())
                self.assertIsNone(resposta.get_json()['telefone'])
                resposta = self.client.put(f"/api/eventos/{evento['id']}", json={
                    'descricao': vazio, 'categoria': vazio, 'imagem_url': vazio,
                })
                self.assertEqual(resposta.status_code, 200, resposta.get_json())
                for campo in ['descricao', 'categoria', 'imagem_url']:
                    self.assertIsNone(resposta.get_json()[campo])
