# Ingresso+

Plataforma web para gestão de eventos e usuários, desenvolvida como projeto
acadêmico. As funcionalidades disponíveis percorrem o fluxo completo:

`Interface React → API Flask → Controller → Service → Model/Repository → PostgreSQL`.

## Integrantes da Equipe

- Bernardo Garajau
- Caio Matos
- Hugo Silva
- Julia Cordeiro
- Luca Torres

## Stack

- **Frontend:** React, Vite, HTML, CSS e Axios
- **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-Migrate e Flask-CORS
- **Banco de dados:** PostgreSQL
- **Infraestrutura:** Docker e Docker Compose

## Arquitetura

O projeto separa as responsabilidades por camada:

```text
backend/
└── app/
    ├── controllers/   # classes que recebem HTTP e retornam respostas da API
    ├── services/      # uma classe por caso de uso; valida e coordena a ação
    ├── models/        # entidades SQLAlchemy e operações CRUD convencionais
    ├── repositories/  # consultas especiais (busca e filtros), sem regra de negócio
    ├── utils/         # validações e erros compartilhados
    ├── extensions.py
    └── __init__.py    # application factory e registro dos blueprints
frontend/
└── src/
    ├── api/           # consumo centralizado da API Flask
    ├── components/    # componentes reutilizáveis
    └── pages/         # telas de usuários e eventos
```

As Controllers não executam SQL nem regras de negócio. Os Services executam a
validação de cada caso de uso e acionam Models para CRUD convencional ou
Repositories para as consultas especializadas. As telas consomem somente a
API, sem acesso direto ao banco.

## Como executar

1. Crie o arquivo de variáveis de ambiente a partir do exemplo:

```bash
cp .env.example .env
```

No PowerShell, se necessário:

```powershell
Copy-Item .env.example .env
```

2. Suba os serviços:

```bash
docker compose up --build -d
```

3. Aplique as migrations já versionadas no repositório:

```bash
docker compose exec backend flask db upgrade
```

> Não execute `flask db init`: a pasta `backend/migrations` já existe e faz
> parte do projeto. Ao criar uma alteração futura de schema, gere apenas a nova
> migration com `flask db migrate -m "descricao"` e aplique-a com
> `flask db upgrade`.

4. Acesse:

- Frontend: http://localhost:5173
- API/health: http://localhost:5000/api/health
- PostgreSQL: `localhost:5433`

## Funcionalidades Implementadas

1. Cadastrar usuário
2. Listar usuários
3. Atualizar usuário
4. Excluir usuário
5. Buscar usuários por nome ou e-mail
6. Cadastrar evento
7. Listar eventos
8. Atualizar evento
9. Excluir evento
10. Filtrar eventos por categoria, local ou status

## Endpoints da API

| Recurso | Método | Rota | Descrição |
|---|---|---|---|
| Saúde | GET | `/api/health` | Verifica se a API está disponível |
| Usuários | GET | `/api/usuarios` | Lista usuários |
| Usuários | GET | `/api/usuarios/busca?termo={nome-ou-email}` | Busca por nome ou e-mail |
| Usuários | GET | `/api/usuarios/{id}` | Busca um usuário por identificador |
| Usuários | POST | `/api/usuarios` | Cadastra usuário |
| Usuários | PUT | `/api/usuarios/{id}` | Atualiza usuário |
| Usuários | DELETE | `/api/usuarios/{id}` | Exclui usuário |
| Eventos | GET | `/api/eventos` | Lista eventos |
| Eventos | GET | `/api/eventos/filtro?categoria={categoria}&local={local}&status={status}` | Filtra por categoria, local e/ou status |
| Eventos | GET | `/api/eventos/{id}` | Busca um evento por identificador |
| Eventos | POST | `/api/eventos` | Cadastra evento |
| Eventos | PUT | `/api/eventos/{id}` | Atualiza evento |
| Eventos | DELETE | `/api/eventos/{id}` | Exclui evento |

O parâmetro `termo` da busca de usuários é obrigatório. Os filtros de eventos
são opcionais e combináveis; `status` aceita `ativo` ou `inativo`.

## Testes e verificação

Com os containers em execução, verifique a compilação das aplicações:

```bash
docker compose exec backend python -m compileall app
docker compose exec frontend npm run build
```

Execute também a suíte automatizada da API:

```bash
docker compose exec backend python -m unittest discover -s tests -v
```

Depois, valide pela interface os seguintes cenários de ponta a ponta:

| Cenário | Resultado esperado |
|---|---|
| Cadastrar usuário | O formulário cria o registro e ele aparece na listagem |
| Editar/excluir usuário | A alteração aparece na lista; a exclusão remove o registro |
| Buscar usuário | A busca retorna usuários cujo nome ou e-mail corresponde ao termo |
| Cadastrar evento | O formulário cria o evento e ele aparece na listagem |
| Editar/excluir evento | A alteração aparece na lista; a exclusão remove o evento |
| Filtrar eventos | Categoria, local e status retornam somente os eventos compatíveis |

## Roteiro objetivo para o vídeo (até 5 minutos)

1. **0:00–0:25** — Apresente o projeto, a arquitetura em camadas e a tela inicial.
2. **0:25–1:40** — Cadastre um usuário, mostre-o na listagem, pesquise por nome
   ou e-mail, edite e exclua o registro.
3. **1:40–3:10** — Cadastre um evento, mostre-o na listagem, aplique filtros de
   categoria/local/status, edite e exclua o registro.
4. **3:10–4:10** — Mostre rapidamente as chamadas da API no navegador ou no
   DevTools, evidenciando que o frontend consome o backend.
5. **4:10–5:00** — Mostre a organização `controllers`, `services`, `models` e
   `repositories`, reforçando que busca e filtros passam pelo Repository.

## Próximas etapas

- [Roadmap do projeto](docs/roadmap.md)
- [Checklist de fases](docs/FASES.md)
