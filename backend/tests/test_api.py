"""Testes reais da API e MySQL, executados somente no banco isolado ingressos_test."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


# Permite executar tanto em ``backend/`` quanto na raiz do repositório.
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app import create_app  # noqa: E402
from app.config import Config
from app.extensions import obter_conexao, criar_tabelas, consultar, executar  # noqa: E402


class ApiTestCase(unittest.TestCase):
    """Base isolada com uma aplicação Flask e banco temporário por suíte."""

    @classmethod
    def setUpClass(cls):
        class TestConfig(Config):
            TESTING = True
            CORS_ORIGINS = 'http://frontend.test'

        cls.app = create_app(TestConfig)
        if not cls.app.config['DB_NAME'].endswith('_test'):
            raise RuntimeError('Execute a suíte no serviço testes, com banco terminado em _test.')
        with cls.app.app_context():
            criar_tabelas()
        cls.client = cls.app.test_client()

    def setUp(self):
        self.contexto = self.app.app_context()
        self.contexto.push()
        self.addCleanup(self.contexto.pop)
        conexao = obter_conexao()
        with conexao.cursor() as cursor:
            cursor.execute('SET FOREIGN_KEY_CHECKS = 0')
            for tabela in ['auditoria', 'cofre_dados', 'alertas', 'grupo_membros', 'grupos',
                           'ingressos', 'pagamentos', 'reservas', 'documentos_meia', 'assentos', 'lotes', 'eventos', 'usuarios']:
                cursor.execute('TRUNCATE TABLE ' + tabela)
            cursor.execute('SET FOREIGN_KEY_CHECKS = 1')
        from app.models.usuario import Usuario
        from werkzeug.security import generate_password_hash
        admin = Usuario(nome='Administrador dos testes', email='admin@teste.local', cpf='93541134780',
                        senha_hash=generate_password_hash('senha-admin')).salvar()
        executar("UPDATE usuarios SET papel = 'admin' WHERE id = %s", (admin.id,))
        resposta = self.client.post('/api/auth/login', json={'email': admin.email, 'senha': 'senha-admin'})
        self.assertEqual(resposta.status_code, 200)

    def criar_usuario(self, **overrides):
        dados = {
            "nome": "Ana Silva",
            "email": "ana.silva@example.com",
            "cpf": "52998224725",
            "telefone": "11999990000",
            "senha": "senha-segura",
        }
        dados.update(overrides)
        response = self.client.post("/api/usuarios", json=dados)
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()

    def criar_evento(self, **overrides):
        dados = {
            "nome": "Festival de Música",
            "descricao": "Um grande festival ao ar livre.",
            "local": "Teatro Municipal",
            "categoria": "Música",
            "imagem_url": "https://example.com/festival.png",
            "data_hora_evento": "2026-12-15T20:00:00",
            "data_abertura_vendas": "2026-10-01T09:00:00",
        }
        dados.update(overrides)
        response = self.client.post("/api/eventos", json=dados)
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()


class UsuarioApiTest(ApiTestCase):
    """Seis casos de uso completos do recurso usuário."""

    def test_01_criar_usuario(self):
        usuario = self.criar_usuario()

        self.assertIsInstance(usuario["id"], int)
        self.assertEqual(usuario["nome"], "Ana Silva")
        self.assertEqual(usuario["email"], "ana.silva@example.com")
        self.assertNotIn("senha", usuario)
        self.assertNotIn("senha_hash", usuario)

    def test_02_listar_usuarios_com_cors(self):
        self.criar_usuario()
        self.criar_usuario(
            nome="Bruno Costa",
            email="bruno.costa@example.com",
            cpf="11144477735",
        )

        response = self.client.get(
            "/api/usuarios", headers={"Origin": "http://frontend.test"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 3)
        self.assertEqual(
            response.headers.get("Access-Control-Allow-Origin"), "http://frontend.test"
        )

    def test_03_buscar_usuario_por_id(self):
        usuario = self.criar_usuario()

        response = self.client.get(f"/api/usuarios/{usuario['id']}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["id"], usuario["id"])

    def test_04_atualizar_usuario(self):
        usuario = self.criar_usuario()

        response = self.client.put(
            f"/api/usuarios/{usuario['id']}",
            json={"nome": "Ana Souza", "telefone": "21988887777"},
        )

        self.assertEqual(response.status_code, 200, response.get_json())
        atualizado = response.get_json()
        self.assertEqual(atualizado["nome"], "Ana Souza")
        self.assertEqual(atualizado["telefone"], "21988887777")

    def test_05_remover_usuario(self):
        usuario = self.criar_usuario()

        response = self.client.delete(f"/api/usuarios/{usuario['id']}")

        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.client.get(f"/api/usuarios/{usuario['id']}").status_code, 404)

    def test_06_buscar_usuarios_por_termo_case_insensitive(self):
        self.criar_usuario(nome="Mariana Lima", email="mariana.lima@example.com")
        self.criar_usuario(
            nome="Carlos Rocha",
            email="carlos.rocha@outraempresa.com",
            cpf="11144477735",
        )

        por_nome = self.client.get("/api/usuarios/busca?termo=MARIA")
        por_email = self.client.get("/api/usuarios/busca?termo=OUTRAEMPRESA")

        self.assertEqual(por_nome.status_code, 200, por_nome.get_json())
        self.assertEqual([u["email"] for u in por_nome.get_json()], ["mariana.lima@example.com"])
        self.assertEqual(por_email.status_code, 200, por_email.get_json())
        self.assertEqual([u["nome"] for u in por_email.get_json()], ["Carlos Rocha"])

    def test_07_validacoes_duplicidade_e_usuario_inexistente(self):
        self.criar_usuario()

        duplicado = self.client.post(
            "/api/usuarios",
            json={
                "nome": "Outra Ana",
                "email": "ana.silva@example.com",
                "cpf": "11144477735",
                "senha": "senha-segura",
            },
        )
        invalido = self.client.post("/api/usuarios", json={"nome": "Sem dados"})
        busca_sem_termo = self.client.get("/api/usuarios/busca?termo=")
        inexistente = self.client.get("/api/usuarios/999999")

        self.assertEqual(duplicado.status_code, 409)
        self.assertEqual(invalido.status_code, 400)
        self.assertEqual(busca_sem_termo.status_code, 400)
        self.assertEqual(inexistente.status_code, 404)


class EventoApiTest(ApiTestCase):
    """Seis casos de uso completos do recurso evento."""

    def test_08_criar_evento(self):
        evento = self.criar_evento()

        self.assertIsInstance(evento["id"], int)
        self.assertEqual(evento["nome"], "Festival de Música")
        self.assertEqual(evento["categoria"], "Música")

    def test_09_listar_eventos(self):
        self.criar_evento()
        self.criar_evento(
            nome="Peça de Teatro",
            local="Teatro Central",
            categoria="Teatro",
            data_hora_evento="2026-12-20T20:00:00",
        )

        response = self.client.get("/api/eventos")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 2)

    def test_10_buscar_evento_por_id(self):
        evento = self.criar_evento()

        response = self.client.get(f"/api/eventos/{evento['id']}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["id"], evento["id"])

    def test_11_atualizar_evento(self):
        evento = self.criar_evento()

        response = self.client.put(
            f"/api/eventos/{evento['id']}",
            json={"nome": "Festival Atualizado", "categoria": "Shows"},
        )

        self.assertEqual(response.status_code, 200, response.get_json())
        self.assertEqual(response.get_json()["nome"], "Festival Atualizado")
        self.assertEqual(response.get_json()["categoria"], "Shows")

    def test_12_remover_evento(self):
        evento = self.criar_evento()

        response = self.client.delete(f"/api/eventos/{evento['id']}")

        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.client.get(f"/api/eventos/{evento['id']}").status_code, 404)

    def test_13_filtrar_eventos_por_categoria_local_e_status(self):
        correspondente = self.criar_evento()
        self.criar_evento(
            nome="Show em outro local",
            local="Arena Norte",
            data_hora_evento="2026-12-16T20:00:00",
        )
        inativo = self.criar_evento(
            nome="Festival Encerrado",
            data_hora_evento="2026-12-17T20:00:00",
        )
        desativacao = self.client.put(f"/api/eventos/{inativo['id']}", json={"ativo": False})
        self.assertEqual(desativacao.status_code, 200, desativacao.get_json())

        ativos = self.client.get(
            "/api/eventos/filtro?categoria=M%C3%BAsica&local=Teatro%20Municipal&status=ativo"
        )
        inativos = self.client.get("/api/eventos/filtro?status=inativo")

        self.assertEqual(ativos.status_code, 200, ativos.get_json())
        self.assertEqual([e["id"] for e in ativos.get_json()], [correspondente["id"]])
        self.assertEqual(inativos.status_code, 200, inativos.get_json())
        self.assertEqual([e["id"] for e in inativos.get_json()], [inativo["id"]])

    def test_14_validacao_de_datas_e_evento_inexistente(self):
        invalido = self.client.post(
            "/api/eventos",
            json={
                "nome": "Evento Inválido",
                "local": "Auditório",
                "data_hora_evento": "2026-12-01T20:00:00",
                "data_abertura_vendas": "2026-12-02T09:00:00",
            },
        )
        inexistente = self.client.get("/api/eventos/999999")

        self.assertEqual(invalido.status_code, 400)
        self.assertEqual(inexistente.status_code, 404)


class RelatorioEventosApiTest(ApiTestCase):
    """Consulta agregada que percorre Controller -> Service -> Repository."""

    def test_15_relatorio_eventos_vazio(self):
        response = self.client.get("/api/relatorios/eventos")

        self.assertEqual(response.status_code, 200, response.get_json())
        self.assertEqual(
            response.get_json(),
            {
                "total_eventos": 0,
                "total_ativos": 0,
                "total_inativos": 0,
                "categorias": [],
            },
        )

    def test_16_relatorio_eventos_por_categoria_e_status(self):
        self.criar_evento()
        musica_inativo = self.criar_evento(
            nome="Show Musical Encerrado",
            categoria="Música",
            data_hora_evento="2026-12-16T20:00:00",
        )
        teatro_inativo = self.criar_evento(
            nome="Peça Encerrada",
            categoria="Teatro",
            data_hora_evento="2026-12-17T20:00:00",
        )
        self.criar_evento(
            nome="Evento Sem Categoria",
            categoria=None,
            data_hora_evento="2026-12-18T20:00:00",
        )
        for evento in (musica_inativo, teatro_inativo):
            resposta = self.client.put(f"/api/eventos/{evento['id']}", json={"ativo": False})
            self.assertEqual(resposta.status_code, 200, resposta.get_json())

        response = self.client.get("/api/relatorios/eventos")

        self.assertEqual(response.status_code, 200, response.get_json())
        relatorio = response.get_json()
        self.assertEqual(relatorio["total_eventos"], 4)
        self.assertEqual(relatorio["total_ativos"], 2)
        self.assertEqual(relatorio["total_inativos"], 2)

        categorias = {item["categoria"]: item for item in relatorio["categorias"]}
        self.assertEqual(
            categorias,
            {
                "Música": {"categoria": "Música", "total": 2, "ativos": 1, "inativos": 1},
                "Teatro": {"categoria": "Teatro", "total": 1, "ativos": 0, "inativos": 1},
                "Sem categoria": {
                    "categoria": "Sem categoria",
                    "total": 1,
                    "ativos": 1,
                    "inativos": 0,
                },
            },
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
