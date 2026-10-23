# Ambiente local no Windows

## Iniciar

O `.env` desta máquina já está configurado. Preserve o arquivo e as chaves.

```powershell
docker compose up --build -d
docker compose exec backend flask criar-demo
docker compose ps
```

O comando `criar-demo` é opcional e cria dados fictícios sem modificar os
registros anteriores. Contas `admin@ingressoplus.local` e
`cliente@ingressoplus.local`, senha `DemoIngresso123!`.

- Interface: http://localhost:5173
- API: http://localhost:5000/api/health
- MySQL: localhost:3307
- O worker entrega avisos dentro do sistema e expira reservas a cada 10 segundos.

As tabelas e a Stored Procedure são criadas na inicialização. O primeiro usuário
anterior recebe papel de administrador na primeira atualização. Use as contas
de demonstração para testar sem precisar alterar a senha de outra conta.

## Testar sem afetar os dados

```powershell
docker compose --profile testes run --build --rm testes
docker compose exec frontend npm run build
docker compose exec backend python -m compileall app
docker compose --profile testes stop db_test
```

A suíte usa outro container MySQL, com banco ingressos_test e dados temporários.
Ela não deve ser executada no backend ligado ao banco principal.

## Persistência e backups

O nome local do projeto Docker continua `projetodesoftware`, definido por
COMPOSE_PROJECT_NAME. O volume ativo é `projetodesoftware_mysql_data`.
O volume antigo `projetodesoftware_postgres_data` foi preservado, separado.

Backups locais ignorados pelo Git:

- backups/ingressoplus-before-mysql.dump
- backups/dados-postgres-antes-mysql.json
- backups/ingressoplus-antes-20-funcoes.sql

A importação do PostgreSQL para MySQL já foi executada e conferida. O importador
em migrations/importar_postgres.py exige tabelas vazias e não deve ser repetido
em um banco preenchido.

## Desenvolvimento

As pastas backend e frontend são montadas nos containers. O Vite recarrega a
interface. Após editar Python, reinicie backend e worker; após mudar dependências,
reconstrua as imagens.

```powershell
docker compose restart backend worker
docker compose logs --tail 100 backend worker frontend
docker compose stop
```

As chaves SECRET_KEY e COFRE_SECRET_KEY devem permanecer estáveis no .env.
A chave do cofre permite ler o conteúdo criptografado. Não a publique no GitHub.
Pagamentos e estornos são apenas simulados; nenhum cartão é solicitado.
