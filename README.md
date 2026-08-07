# Ingresso+

Plataforma web voltada para a gestão e venda de ingressos de eventos,
desenvolvida como projeto acadêmico e dividida em partes. Esta primeira etapa
entrega a estrutura completa do projeto e o CRUD base de **Eventos** e
**Usuários** (Models, Services, Controllers e frontend consumindo a API).

## Integrantes da Equipe

- Bernardo Garajau
- Caio Matos
- Hugo Silva
- Julia Cordeiro
- Luca Torres

## Stack

- **Frontend:** HTML5, CSS3, JavaScript, React (Vite)
- **Backend:** Python (Flask), arquitetura em camadas (Models → Services → Controllers)
- **Banco de dados:** PostgreSQL
- **Infraestrutura:** Docker / Docker Compose

## Estrutura de pastas

```
Projeto de Software/
├── backend/
│   ├── app/
│   │   ├── controllers/   # Blueprints Flask (rotas HTTP)
│   │   ├── services/      # Regras de negocio e validacoes
│   │   ├── models/        # Modelos SQLAlchemy
│   │   ├── utils/         # Validadores e erros compartilhados
│   │   ├── config.py
│   │   └── __init__.py    # Application factory
│   ├── run.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/           # Camada de consumo da API (axios)
│   │   ├── components/    # Componentes reutilizaveis (Navbar, etc.)
│   │   └── pages/         # Telas de Eventos e Usuarios (CRUD)
│   ├── package.json
│   └── Dockerfile
├── docs/
│   └── roadmap.md         # Requisitos das proximas etapas do projeto
├── docker-compose.yml
└── .env.example
```

## Como rodar com Docker

1. Copie o arquivo de variáveis de ambiente:

```bash
cp .env.example .env
```

2. Suba os containers:

```bash
docker compose up --build
```

3. Na primeira vez, crie as tabelas do banco (em outro terminal):

```bash
docker compose exec backend flask db init
docker compose exec backend flask db migrate -m "tabelas iniciais"
docker compose exec backend flask db upgrade
```

4. Acesse:
   - Frontend: http://localhost:5173
   - Backend (API): http://localhost:5000/api/health
   - PostgreSQL (para um cliente externo, ex. DBeaver): localhost:5433

> A porta do Postgres é 5433 (em vez da padrão 5432) porque a 5432 já está em
> uso por outro projeto local. Se não for o seu caso, pode voltar para 5432
> em `docker-compose.yml`.

## Endpoints implementados (Parte 1)

| Recurso  | Método | Rota                  | Descrição            |
|----------|--------|------------------------|-----------------------|
| Eventos  | GET    | /api/eventos           | Listar eventos        |
| Eventos  | GET    | /api/eventos/`<id>`    | Buscar evento         |
| Eventos  | POST   | /api/eventos           | Criar evento          |
| Eventos  | PUT    | /api/eventos/`<id>`    | Atualizar evento      |
| Eventos  | DELETE | /api/eventos/`<id>`    | Remover evento        |
| Usuarios | GET    | /api/usuarios          | Listar usuarios       |
| Usuarios | GET    | /api/usuarios/`<id>`   | Buscar usuario        |
| Usuarios | POST   | /api/usuarios          | Criar usuario         |
| Usuarios | PUT    | /api/usuarios/`<id>`   | Atualizar usuario     |
| Usuarios | DELETE | /api/usuarios/`<id>`   | Remover usuario       |

## Próximas partes

- [docs/roadmap.md](docs/roadmap.md) — requisitos levantados para as próximas etapas.
- [docs/FASES.md](docs/FASES.md) — checklist passo a passo para acompanhar o desenvolvimento por fases.
