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
    ├── repositories/  # consultas especiais (busca, filtros e relatórios), sem regra de negócio
    ├── utils/         # validações e erros compartilhados
    ├── extensions.py
    └── __init__.py    # application factory e registro dos blueprints
frontend/
└── src/
    ├── api/           # consumo centralizado da API Flask
    ├── components/    # componentes reutilizáveis
    └── pages/         # telas de usuários, eventos e relatórios
```

As Controllers não executam SQL nem regras de negócio. Os Services executam a
validação de cada caso de uso e acionam Models para CRUD convencional ou
Repositories para as consultas especializadas. As telas consomem somente a
API, sem acesso direto ao banco. As listagens exibem o **ID** de cada usuário
e evento, tornando identificadores e consultas individuais verificáveis na
interface.

O relatório de eventos é uma consulta agregada: a Controller delega a ação a
um Service específico, que usa o Repository para a agregação por categoria e
status. Assim, nenhum `SELECT` ou regra de negócio fica na Controller.

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

## Configuração segura e integrações

Nesta entrega não há integração com IA ou API externa. Caso uma integração
seja adicionada, a comunicação deverá ficar em um Service próprio. Valores de
configuração e credenciais são lidos de variáveis de ambiente: o arquivo `.env`
real é ignorado pelo Git e somente o modelo sem dados sensíveis
`.env.example` é versionado.

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
11. Gerar relatório de eventos por categoria e status

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
| Relatórios | GET | `/api/relatorios/eventos` | Consolida total, ativos, inativos e grupos por categoria/status |

O parâmetro `termo` da busca de usuários é obrigatório. Os filtros de eventos
são opcionais e combináveis; `status` aceita `ativo` ou `inativo`.

O relatório retorna o contrato abaixo; eventos sem categoria aparecem no grupo
`Sem categoria`:

```json
{
  "total_eventos": 4,
  "total_ativos": 2,
  "total_inativos": 2,
  "categorias": [
    { "categoria": "Música", "total": 2, "ativos": 1, "inativos": 1 }
  ]
}
```

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
| Relatório de eventos | Mostra totais ativo/inativo e agrupamento por categoria, incluindo `Sem categoria` |

A suíte também cobre o relatório vazio e a agregação de dados por categoria e
status, além dos fluxos CRUD, busca e filtros. Os testes usam SQLite em memória
e exercitam a API Flask completa, sem depender do PostgreSQL local.

## Vídeo obrigatório — roteiro objetivo (até 5 minutos)

O vídeo é obrigatório para a avaliação. Grave a demonstração abaixo mostrando
o fluxo completo de cada recurso: tela React → chamada da API Flask → resultado
persistido no banco.

1. **0:00–0:20** — Apresente o projeto, a arquitetura em camadas e a tela inicial.
2. **0:20–1:25** — Cadastre um usuário, mostre seu **ID** na listagem, pesquise
   por nome ou e-mail, edite e exclua o registro.
3. **1:25–2:45** — Cadastre dois ou mais eventos, mostre os **IDs** na listagem,
   edite um registro e desative outro.
4. **2:45–3:35** — Aplique filtros de categoria/local/status e abra o relatório,
   destacando totais, ativos, inativos e o grupo `Sem categoria`.
5. **3:35–4:15** — Mostre rapidamente as chamadas da API no navegador ou no
   DevTools, incluindo `GET /api/relatorios/eventos`, para evidenciar o consumo
   do backend pelo frontend.
6. **4:15–5:00** — Mostre `controllers`, `services`, `models` e `repositories`,
   reforçando que filtros e relatório passam pelo Repository; encerre com a
   suíte de testes executada.

## Próximas etapas

- [Roadmap do projeto](docs/roadmap.md)
- [Checklist de fases](docs/FASES.md)
