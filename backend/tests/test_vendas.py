import io
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from unittest.mock import patch

from test_api import ApiTestCase
from app.extensions import consultar, executar
from app.services.reserva_service import expirar_reservas
from app.utils.vendas import agora


class FluxosCompletosTest(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.evento = self.criar_evento()
        resposta = self.client.post(f"/api/eventos/{self.evento['id']}/lotes", json={
            'nome': 'Primeiro lote', 'preco': '100.00', 'quantidade': 10, 'taxa_percentual': 10,
            'inicio': (agora() - timedelta(days=1)).isoformat(),
            'fim': (agora() + timedelta(days=5)).isoformat(),
        })
        self.assertEqual(resposta.status_code, 201, resposta.get_json())
        self.lote = resposta.get_json()
        self.cliente = self.app.test_client()
        resposta = self.cliente.post('/api/auth/cadastro', json={
            'nome': 'Cliente Teste', 'email': 'cliente@teste.local', 'cpf': '52998224725', 'senha': 'senha-cliente',
            'papel': 'admin',
        })
        self.assertEqual(resposta.status_code, 201, resposta.get_json())
        self.usuario = resposta.get_json()

    def reservar(self, cliente=None, **campos):
        return (cliente or self.cliente).post('/api/reservas', json={'lote_id': self.lote['id'], 'quantidade': 1, **campos})

    def outro_cliente(self):
        cliente = self.app.test_client()
        resposta = cliente.post('/api/auth/cadastro', json={'nome': 'Outro Cliente', 'email': 'outro@teste.local',
                                                           'cpf': '11144477735', 'senha': 'senha-cliente'})
        self.assertEqual(resposta.status_code, 201)
        return cliente

    def criar_mapa(self):
        resposta = self.client.post(f"/api/eventos/{self.evento['id']}/assentos", json={'setor': 'Plateia', 'filas': 2, 'por_fila': 3})
        self.assertEqual(resposta.status_code, 201, resposta.get_json())
        return resposta.get_json()

    def documento(self, cliente=None):
        resposta = (cliente or self.cliente).post('/api/meia/documentos', data={
            'arquivo': (io.BytesIO(b'%PDF-1.4\nDocumento ficticio para teste'), 'comprovante.pdf'),
            'tipo': 'estudante', 'validade': '2027-12-31',
        }, content_type='multipart/form-data')
        self.assertEqual(resposta.status_code, 201, resposta.get_json())
        return resposta.get_json()['id']

    def test_cadastro_nao_permite_escalar_permissao(self):
        self.assertEqual(self.usuario['papel'], 'cliente')
        self.assertEqual(self.cliente.get('/api/usuarios').status_code, 403)
        self.assertEqual(self.app.test_client().get('/api/usuarios').status_code, 401)
        self.assertEqual(self.cliente.post('/api/eventos', json={}).status_code, 403)

    def test_login_logout_e_senha_invalida(self):
        cliente = self.app.test_client()
        self.assertEqual(cliente.post('/api/auth/login', json={'email': 'cliente@teste.local', 'senha': 'errada'}).status_code, 401)
        self.assertEqual(cliente.post('/api/auth/login', json={'email': 'cliente@teste.local', 'senha': 'senha-cliente'}).status_code, 200)
        self.assertEqual(cliente.get('/api/auth/sessao').status_code, 200)
        cliente.post('/api/auth/logout')
        self.assertEqual(cliente.get('/api/auth/sessao').status_code, 401)

    def test_origem_estranha_nao_pode_fazer_mutacoes(self):
        resposta = self.cliente.post('/api/reservas', json={'lote_id': self.lote['id']}, headers={'Origin': 'https://outro-site.example'})
        self.assertEqual(resposta.status_code, 403)

    def test_perfil_nao_altera_papel(self):
        resposta = self.cliente.put('/api/perfil', json={'nome': 'Nome Atualizado', 'papel': 'admin'})
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.get_json()['nome'], 'Nome Atualizado')
        self.assertEqual(resposta.get_json()['papel'], 'cliente')

    def test_cofre_criptografado_e_revogacao(self):
        dados = {'consentimento': True, 'endereco': 'Rua Fictícia 10', 'cidade': 'Cidade Teste', 'preferencias': 'Música'}
        self.assertEqual(self.cliente.put('/api/perfil/cofre', json=dados).status_code, 200)
        linha = consultar('SELECT conteudo FROM cofre_dados WHERE usuario_id = %s', (self.usuario['id'],), apenas_um=True)
        self.assertNotIn('Rua Fictícia', linha['conteudo'])
        self.assertEqual(self.cliente.get('/api/perfil/cofre').get_json(), dados)
        self.cliente.put('/api/perfil/cofre', json={'consentimento': False})
        self.assertFalse(self.cliente.get('/api/perfil/cofre').get_json()['consentimento'])
        self.assertIsNone(consultar('SELECT * FROM cofre_dados WHERE usuario_id = %s', (self.usuario['id'],), apenas_um=True))

    def test_exportacao_inclui_somente_dados_proprios(self):
        outro = self.outro_cliente()
        self.reservar()
        dados = outro.get('/api/perfil/exportar').get_json()
        self.assertEqual(dados['perfil']['email'], 'outro@teste.local')
        self.assertEqual(dados['reservas'], [])
        self.assertNotIn('senha_hash', dados['perfil'])
        self.assertTrue(dados['historico'])

    def test_lote_quantidade_precos_e_periodo(self):
        url = f"/api/eventos/{self.evento['id']}/lotes"
        for preco in ['NaN', '-1', 'abc']:
            r = self.client.post(url, json={'nome': 'Inválido', 'preco': preco, 'quantidade': 10,
                                            'inicio': (agora() - timedelta(days=1)).isoformat(), 'fim': (agora() + timedelta(days=1)).isoformat()})
            self.assertEqual(r.status_code, 400)
        executar('UPDATE lotes SET inicio = %s WHERE id = %s', (agora() + timedelta(days=1), self.lote['id']))
        self.assertEqual(self.reservar().status_code, 409)

    def test_comparador_taxas_e_centavos(self):
        linhas = self.cliente.get(f"/api/lotes/{self.lote['id']}/taxas?quantidade=2&tipo=meia").get_json()
        proprio = next(linha for linha in linhas if linha['canal'] == 'Ingresso+')
        self.assertEqual(proprio['subtotal'], '100.00')
        self.assertEqual(proprio['taxa'], '10.00')
        self.assertEqual(proprio['total'], '110.00')

    def test_mapa_stored_procedure_e_reserva_ocupada(self):
        mapa = self.criar_mapa()
        self.assertEqual(len(mapa), 6)
        self.assertTrue(all(item['status'] == 'disponivel' for item in mapa))
        resposta = self.reservar(assento_id=mapa[0]['id'])
        self.assertEqual(resposta.status_code, 201, resposta.get_json())
        self.assertEqual(self.reservar(assento_id=mapa[0]['id']).status_code, 409)
        mapa = self.cliente.get(f"/api/eventos/{self.evento['id']}/assentos").get_json()
        self.assertEqual(mapa[0]['status'], 'ocupado')

    def test_mapa_exige_assento_e_quantidade_um(self):
        mapa = self.criar_mapa()
        self.assertEqual(self.reservar().status_code, 400)
        self.assertEqual(self.reservar(assento_id=mapa[0]['id'], quantidade=2).status_code, 400)
        self.assertEqual(self.client.post(f"/api/eventos/{self.evento['id']}/assentos", json={'setor': 'Outro', 'filas': 1, 'por_fila': 1}).status_code, 409)

    def test_estoque_concorrente_nao_vende_acima_da_capacidade(self):
        executar('UPDATE lotes SET quantidade = 1 WHERE id = %s', (self.lote['id'],))
        outro = self.outro_cliente()
        with ThreadPoolExecutor(max_workers=2) as pool:
            resultados = list(pool.map(lambda cliente: self.reservar(cliente).status_code, [self.cliente, outro]))
        self.assertEqual(sorted(resultados), [201, 409])

    def test_assento_concorrente_tem_um_unico_comprador(self):
        mapa = self.criar_mapa()
        outro = self.outro_cliente()
        with ThreadPoolExecutor(max_workers=2) as pool:
            resultados = list(pool.map(lambda cliente: self.reservar(cliente, assento_id=mapa[0]['id']).status_code, [self.cliente, outro]))
        self.assertEqual(sorted(resultados), [201, 409])

    def test_expiracao_libera_estoque_e_bloqueia_pagamento(self):
        executar('UPDATE lotes SET quantidade = 1 WHERE id = %s', (self.lote['id'],))
        reserva = self.reservar().get_json()
        executar('UPDATE reservas SET expira_em = %s WHERE id = %s', (agora() - timedelta(seconds=1), reserva['id']))
        expirar_reservas()
        self.assertEqual(self.cliente.post(f"/api/reservas/{reserva['id']}/pagamento", json={}).status_code, 409)
        self.assertEqual(self.reservar().status_code, 201)

    def test_pagamento_idempotente_emite_uma_unica_vez(self):
        reserva = self.reservar(quantidade=2).get_json()
        url = f"/api/reservas/{reserva['id']}/pagamento"
        for _ in range(2):
            self.assertEqual(self.cliente.post(url, json={'resultado': 'aprovado'}).status_code, 200)
        self.assertEqual(len(self.cliente.get('/api/ingressos').get_json()), 2)
        self.assertEqual(consultar('SELECT COUNT(*) AS total FROM pagamentos', apenas_um=True)['total'], 1)

    def test_recusa_permite_tentar_novamente(self):
        reserva = self.reservar().get_json()
        url = f"/api/reservas/{reserva['id']}/pagamento"
        self.assertEqual(self.cliente.post(url, json={'resultado': 'recusado'}).get_json()['status'], 'recusado')
        self.assertEqual(self.cliente.get('/api/ingressos').get_json(), [])
        self.assertEqual(self.cliente.post(url, json={'resultado': 'aprovado'}).get_json()['status'], 'aprovado')
        self.assertEqual(len(self.cliente.get('/api/ingressos').get_json()), 1)

    def test_cancelamento_pago_estorna_e_invalida_ingresso(self):
        reserva = self.reservar().get_json()
        self.cliente.post(f"/api/reservas/{reserva['id']}/pagamento", json={})
        ingresso = self.cliente.get('/api/ingressos').get_json()[0]
        self.assertEqual(self.cliente.post(f"/api/reservas/{reserva['id']}/cancelar").status_code, 200)
        self.assertEqual(self.client.post('/api/ingressos/validar', json={'codigo': ingresso['codigo']}).status_code, 409)
        self.assertEqual(consultar('SELECT status FROM pagamentos', apenas_um=True)['status'], 'estornado')

    def test_validacao_bloqueia_reuso_e_cancelamento(self):
        reserva = self.reservar().get_json()
        self.cliente.post(f"/api/reservas/{reserva['id']}/pagamento", json={})
        ingresso = self.cliente.get('/api/ingressos').get_json()[0]
        self.assertEqual(self.client.post('/api/ingressos/validar', json={'codigo': ingresso['codigo']}).status_code, 200)
        self.assertEqual(self.client.post('/api/ingressos/validar', json={'codigo': ingresso['codigo']}).status_code, 409)
        self.assertEqual(self.cliente.post(f"/api/reservas/{reserva['id']}/cancelar").status_code, 409)

    def test_privacidade_de_reservas_e_documentos(self):
        outro = self.outro_cliente()
        reserva = self.reservar().get_json()
        self.assertEqual(outro.post(f"/api/reservas/{reserva['id']}/cancelar").status_code, 404)
        self.assertEqual(outro.post(f"/api/reservas/{reserva['id']}/pagamento", json={}).status_code, 404)
        doc = self.documento()
        self.assertEqual(outro.get(f'/api/meia/documentos/{doc}/arquivo').status_code, 404)

    def test_meia_exige_aprovacao_e_aplica_desconto(self):
        self.assertEqual(self.reservar(tipo='meia').status_code, 409)
        doc = self.documento()
        self.assertEqual(self.reservar(tipo='meia').status_code, 409)
        self.assertEqual(self.client.put(f'/api/meia/documentos/{doc}', json={'status': 'aprovado'}).status_code, 200)
        reserva = self.reservar(tipo='meia')
        self.assertEqual(reserva.status_code, 201)
        self.assertEqual(reserva.get_json()['total'], '55.00')

    def test_documento_invalido_e_rejeicao_com_motivo(self):
        r = self.cliente.post('/api/meia/documentos', data={'arquivo': (io.BytesIO(b'<script>teste</script>'), 'falso.pdf'), 'tipo': 'estudante', 'validade': '2027-12-31'}, content_type='multipart/form-data')
        self.assertEqual(r.status_code, 400)
        doc = self.documento()
        self.assertEqual(self.client.put(f'/api/meia/documentos/{doc}', json={'status': 'rejeitado'}).status_code, 400)
        self.assertEqual(self.client.put(f'/api/meia/documentos/{doc}', json={'status': 'rejeitado', 'observacao': 'Documento ilegível'}).status_code, 200)

    def test_compra_expressa_atomica(self):
        url = '/api/checkout/expressa'
        dados = {'lote_id': self.lote['id'], 'quantidade': 1}
        self.assertEqual(self.cliente.post(url, json=dados).status_code, 400)
        self.assertEqual(self.cliente.post(url, json={**dados, 'confirmar_simulacao': True}).status_code, 201)
        self.assertEqual(len(self.cliente.get('/api/ingressos').get_json()), 1)
        with patch.dict(self.app.config, MODO_DEMONSTRACAO=False):
            self.assertEqual(self.cliente.post(url, json={**dados, 'confirmar_simulacao': True}).status_code, 503)
        self.assertEqual(consultar('SELECT COUNT(*) AS total FROM reservas', apenas_um=True)['total'], 1)

    def test_grupo_participacao_e_privacidade(self):
        resposta = self.cliente.post('/api/grupos', json={'nome': 'Amigos', 'evento_id': self.evento['id']})
        self.assertEqual(resposta.status_code, 201, resposta.get_json())
        grupo = resposta.get_json()
        outro = self.outro_cliente()
        self.assertEqual(outro.get(f"/api/grupos/{grupo['id']}").status_code, 404)
        self.assertEqual(outro.post('/api/grupos/entrar', json={'codigo': grupo['codigo']}).status_code, 200)
        self.assertEqual(len(outro.get(f"/api/grupos/{grupo['id']}").get_json()['membros']), 2)
        self.assertEqual(self.cliente.post(f"/api/grupos/{grupo['id']}/sair").status_code, 409)
        self.assertEqual(outro.post(f"/api/grupos/{grupo['id']}/sair").status_code, 200)

    def test_alerta_entrega_leitura_e_duplicidade(self):
        dados = {'evento_id': self.evento['id'], 'agendado_em': (agora() + timedelta(hours=1)).isoformat()}
        resposta = self.cliente.post('/api/alertas', json=dados)
        self.assertEqual(resposta.status_code, 201)
        self.assertEqual(self.cliente.post('/api/alertas', json=dados).status_code, 409)
        alerta_id = resposta.get_json()['id']
        executar('UPDATE alertas SET agendado_em = %s WHERE id = %s', (agora() - timedelta(seconds=1), alerta_id))
        self.assertEqual(self.cliente.get('/api/alertas').get_json()[0]['status'], 'enviado')
        self.assertEqual(self.cliente.put(f'/api/alertas/{alerta_id}', json={'acao': 'ler'}).status_code, 200)
        self.assertTrue(self.cliente.get('/api/alertas').get_json()[0]['lido'])

    def test_recomendacao_local_por_preferencia(self):
        self.cliente.put('/api/perfil/cofre', json={'consentimento': True, 'preferencias': 'Música'})
        resposta = self.cliente.get('/api/recomendacoes')
        self.assertEqual(resposta.status_code, 200)
        self.assertIn('local', resposta.get_json()['origem'])
        self.assertGreater(resposta.get_json()['eventos'][0]['pontos'], 0)

    def test_relatorio_nao_multiplica_valor_por_ingresso(self):
        reserva = self.reservar(quantidade=3).get_json()
        self.cliente.post(f"/api/reservas/{reserva['id']}/pagamento", json={})
        url = f"/api/relatorios/vendas/{self.evento['id']}"
        self.assertEqual(self.cliente.get(url).status_code, 403)
        resumo = self.client.get(url).get_json()
        self.assertEqual(resumo['compras'], 1)
        self.assertEqual(str(resumo['ingressos']), '3')
        self.assertEqual(resumo['arrecadacao'], '330.00')
        self.cliente.post(f"/api/reservas/{reserva['id']}/cancelar")
        self.assertEqual(self.client.get(url).get_json()['arrecadacao'], '0.00')

    def test_exclusao_nao_apaga_historico_de_vendas(self):
        self.reservar()
        self.assertEqual(self.client.delete(f"/api/eventos/{self.evento['id']}").status_code, 409)
        self.assertEqual(self.client.delete(f"/api/usuarios/{self.usuario['id']}").status_code, 409)
