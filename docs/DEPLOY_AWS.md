# IngressoPlus na AWS EC2

Configuração para uma única EC2 com **Ubuntu 24.04 e 4 GB de RAM**, usando a
branch `deploy/aws`. Este guia contém comandos para execução manual após revisão;
nenhuma ação na AWS é feita pela configuração do repositório.

## Arquitetura e isolamento

```text
Internet -> porta 80 -> frontend (Nginx + React compilado)
                              -> /api/ -> backend (Gunicorn/Flask)
                                                   -> MySQL
                                                      ^
                                                    worker
```

- Somente o frontend publica porta no host. Backend, MySQL, worker e `init_db`
  não possuem `ports`. A rede `database` é interna; o frontend não participa dela.
- `VITE_API_URL=/api` é definido no build. Axios acrescenta caminhos como
  `/auth/login`, resultando em `/api/auth/login`. O `proxy_pass` do Nginx não
  acrescenta nem remove `/api`. Não configure `/api/api` ou a URL de localhost.
- `PUBLIC_ORIGIN` deve corresponder exatamente à origem no navegador, por exemplo
  `http://203.0.113.10`, sem barra final nem `/api`. A aplicação verifica o
  cabeçalho `Origin` também quando frontend e API estão na mesma origem.
- Cookies HttpOnly e SameSite=Lax continuam como no ambiente local. Nesta etapa
  HTTP, não recebem `Secure`; o tráfego não é criptografado. Use dados fictícios
  e configure HTTPS antes de trabalhar com credenciais ou dados reais.
- Pagamentos continuam **simulados**, com `MODO_DEMONSTRACAO=true` fixado no
  Compose. Definir `false` impediria pagamentos e compra expressa nesta versão.
  Nenhuma conta demo é criada automaticamente.
- Gemini permanece desligado por padrão. Somente o backend recebe sua chave e
  tem uma rede com saída para a internet. O worker mantém suas tarefas locais.

Use o Compose de produção **isoladamente**, nunca como override do Compose local.
O nome padrão do projeto é `ingressoplus-prod`, com volume
`ingressoplus-prod_mysql_data`. Mantenha esse nome: alterá-lo cria outro volume.
O desenvolvimento continua usando `docker-compose.yml` e os Dockerfiles antigos.

## Preparar a instância

1. Crie a EC2 Ubuntu 24.04 com 4 GB de RAM, armazenamento EBS dimensionado para
   banco, imagens, logs e backups, e acesso à internet por IP público.
2. No Security Group, libere TCP 80 para os visitantes e TCP 22 somente para o
   IP administrativo. Não libere 3306, 3307, 5000 ou 5173. Para IPv6, configure
   regras equivalentes somente se for utilizá-lo. A porta 443 fica para HTTPS.
3. Prefira um IP estável, como Elastic IP. Se o IP mudar, atualize `PUBLIC_ORIGIN`
   e recrie o backend. A interface usa URL relativa e não exige novo build.
4. Instale Docker Engine e o plugin Docker Compose seguindo o
   [guia oficial para Ubuntu](https://docs.docker.com/engine/install/ubuntu/).
   Use Compose v2.20 ou posterior e verifique:

   ```bash
   sudo systemctl enable --now docker
   sudo docker version
   sudo docker compose version
   ```

Não dependa apenas do UFW para proteger portas publicadas por Docker. A primeira
barreira é publicar apenas a porta necessária e limitar o Security Group.
Os comandos seguintes usam `sudo docker`; acesso ao grupo `docker` equivale a
privilégios administrativos no host.

## Código e variáveis

Obtenha o repositório e selecione exclusivamente a branch de hospedagem:

```bash
git clone --branch deploy/aws --single-branch URL_DO_REPOSITORIO IngressoPlus
cd IngressoPlus
git branch --show-current
umask 077
cp .env.production.example .env.production
chmod 600 .env.production
```

Preencha `.env.production` diretamente no servidor. Ele é ignorado pelo Git e não
entra nas imagens. Não publique a saída de `docker compose config`, pois ela
contém as variáveis interpoladas; use `config --quiet` para validar.

| Variável | Valor |
|---|---|
| `PUBLIC_ORIGIN` | `http://IP_PUBLICO`, sem barra final |
| `HTTP_PORT` | `80` nesta implantação |
| `MYSQL_USER` / `MYSQL_DATABASE` | Nomes próprios, diferentes de `root` |
| `MYSQL_PASSWORD` | Senha forte e exclusiva do usuário da aplicação |
| `MYSQL_ROOT_PASSWORD` | Outra senha forte, usada somente pelo MySQL |
| `SECRET_KEY` | Chave aleatória, longa e persistente para as sessões |
| `COFRE_SECRET_KEY` | Chave Fernet válida e persistente para os dados do cofre |
| `USAR_GEMINI` | `false`; recomendações locais continuam funcionando |

Os campos secretos vazios fazem o Compose falhar antes de iniciar os serviços.
Não use os valores de desenvolvimento. Valores que contenham `$` ou `#` devem
ficar entre aspas simples no arquivo de ambiente. Nunca coloque segredos em
variáveis `VITE_*`, que são públicas no JavaScript compilado.

Após instalar Docker, gere as chaves sem depender de Python no host:

```bash
sudo docker run --rm python:3.12-slim python -c 'import secrets; print(secrets.token_hex(32))'
```

Use a saída para `SECRET_KEY` e gere senhas independentes com o mesmo comando.
Para gerar uma chave Fernet nova, os 32 bytes aleatórios devem ser codificados
em base64 URL-safe:

```bash
sudo docker run --rm python:3.12-slim python -c 'import base64,secrets; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())'
```

**Se importar um banco existente, preserve a chave do cofre original.** Quando
`COFRE_SECRET_KEY` estava vazio, a aplicação derivava a chave de `SECRET_KEY`.
Nesse caso, gere o valor explícito usando a chave de sessão original, sem
colocá-la no histórico do shell:

```bash
sudo docker run --rm -it python:3.12-slim python -c 'import base64,hashlib,getpass; print(base64.urlsafe_b64encode(hashlib.sha256(getpass.getpass("SECRET_KEY original: ").encode()).digest()).decode())'
```

Guarde banco e chaves em backups separados e protegidos. Trocar a chave sem
recriptografar os dados impede a leitura do cofre. Trocar `MYSQL_PASSWORD` no
arquivo não altera a senha dentro de um volume MySQL já inicializado; faça a
rotação no banco e na configuração de forma coordenada.

## Construir e iniciar

Na raiz do repositório, defina uma função para não omitir arquivo e ambiente:

```bash
dc() { sudo docker compose --env-file .env.production -f docker-compose.prod.yml "$@"; }
dc config --quiet
# Builds em sequência para reduzir o pico de RAM.
dc build init_db
dc build frontend
dc up -d --no-build
dc ps -a
dc logs --tail 100 init_db backend worker frontend
```

O MySQL fica saudável, `init_db` cria o esquema e termina com `Exited (0)`;
backend e worker aguardam essa conclusão. O frontend aguarda o healthcheck do
backend. A inicialização não importa dados locais nem executa `criar-demo`.
`init-db` pode ser repetido para esta versão, mas não substitui migrações SQL
revisadas para futuras alterações de tabelas.

Os limites de RAM dos containers são:

| Serviço | Limite |
|---|---:|
| MySQL | 1536 MiB |
| Backend, dois processos Gunicorn com duas threads cada | 640 MiB |
| Worker, uma única instância | 256 MiB |
| Nginx, um processo worker | 128 MiB |
| `init_db`, temporário | 256 MiB |

São 2560 MiB para os serviços permanentes, deixando espaço para Ubuntu, Docker e
cache. O MySQL usa buffer pool de 512 MiB, até 60 conexões e Performance Schema
desligado. O build Vite limita o heap Node a 512 MiB; isso não é um limite total
do processo e os limites de execução não se aplicam aos builds. Faça builds
sequenciais, evite reconstruir sob carga e acompanhe `free -h`, `df -h` e
`sudo docker stats --no-stream`. Se necessário, construa imagens fora da EC2.
O dimensionamento inicial precisa ser confirmado com a carga esperada.

Logs Docker têm rotação de 10 MiB por arquivo, até três arquivos por container.
Healthchecks indicam problemas, mas não reiniciam automaticamente um processo
travado que permaneça vivo. O healthcheck HTTP da API não consulta o banco;
monitore também o MySQL, logs e andamento das tarefas do worker.

## Administrador inicial

Em um banco novo, cadastre uma conta pela interface. Depois promova somente essa
conta pelo console administrativo do container, sem usar as contas demo de senha
conhecida. O comando abaixo pede o e-mail e usa parâmetros SQL:

```bash
dc exec backend python -c 'from run import app; from app.extensions import consultar,executar; email=input("E-mail cadastrado: ").strip().lower(); ctx=app.app_context(); ctx.push(); usuario=consultar("SELECT id FROM usuarios WHERE email = %s", (email,), apenas_um=True); assert usuario, "Conta não encontrada"; executar("UPDATE usuarios SET papel = %s WHERE id = %s", ("admin", usuario["id"])); print("Administrador configurado"); ctx.pop()'
```

Essa é uma operação manual de provisionamento; o cadastro público mantém as
regras atuais e não concede papel de administrador. Em banco importado, verifique
os administradores existentes e remova ou altere credenciais demo antes de expor
o sistema. Evite executar `flask criar-demo` no servidor público.

## Verificar após iniciar

```bash
curl -fsS http://127.0.0.1/api/health
curl -fsS http://127.0.0.1/eventos > /dev/null
dc exec frontend nginx -t
dc exec db sh -c 'MYSQL_PWD="$MYSQL_PASSWORD" mysql -h 127.0.0.1 -u"$MYSQL_USER" "$MYSQL_DATABASE" -e "SELECT 1"'
dc ps -a
```

No navegador, use `http://IP_PUBLICO` e confira cadastro, login/logout, atualização
direta de `/eventos`, reservas, pagamento simulado, compra expressa e comprovantes
de até 2 MiB. As requisições devem usar `/api/...` na porta pública, sem
`/api/api`, `localhost:5000` ou porta 5173. Teste alertas e expiração após
aproximadamente 15 minutos, verificando os logs do worker. Uma origem diferente
de `PUBLIC_ORIGIN` deve receber 403 nas operações de escrita.

Somente o frontend deve apresentar porta publicada em `dc ps`. A partir de outra
máquina, confirme também que MySQL e a API direta não são acessíveis. Reinicie a
stack sem remover volumes e confirme que os registros continuam presentes.

Para teste local da configuração de produção, use outro arquivo de ambiente
ignorado, com `PUBLIC_ORIGIN=http://localhost:8080` e `HTTP_PORT=8080`, chaves
descartáveis e `-p ingressoplus-prod-teste` para separar o volume. Ajuste a função
`dc` para esse arquivo e projeto; nunca aponte testes destrutivos ao banco real.
A suíte existente usa o Compose de desenvolvimento com um MySQL isolado:

```bash
sudo docker compose -p ingressoplus-regressao --profile testes run --build --rm testes
sudo docker compose -p ingressoplus-regressao --profile testes stop db_test
```

O banco de testes usa `tmpfs` e nome terminado em `_test`. Não execute essa suíte
no serviço backend de produção. Prefira executá-la localmente ou em CI para não
disputar os 4 GB da instância com a aplicação.

## Backups e restauração

O volume persiste após recriar containers e após `dc down`. **Não execute
`dc down -v`, `docker volume rm` ou limpeza de volumes em produção.** EBS e volume
Docker não substituem backup; perder a instância ou o disco pode perder os dados.

Crie backups com permissão restrita, incluindo rotinas e conteúdo binário dos
comprovantes. Suspenda alterações de esquema enquanto o dump estiver em andamento:

```bash
umask 077
mkdir -p backups
backup_file="backups/ingressoplus-$(date -u +%Y%m%dT%H%M%SZ).sql"
if dc exec -T db sh -c 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysqldump -h 127.0.0.1 -uroot --single-transaction --routines --triggers --hex-blob --no-tablespaces --set-gtid-purged=OFF "$MYSQL_DATABASE"' > "$backup_file"; then
  chmod 600 "$backup_file"
  printf 'Backup concluído: %s\n' "$backup_file"
else
  printf 'Backup incompleto; não utilize: %s\n' "$backup_file" >&2
fi
```

Transfira cópias protegidas para fora da instância e valide restauração em uma
stack isolada. Agende backups conforme o uso. Guarde também as chaves, o arquivo
de ambiente e a identificação da versão da aplicação em local protegido.

Para restaurar, faça antes um backup do destino e confirme o arquivo e a stack.
A importação substitui dados com os mesmos nomes de tabelas. Pare quem escreve,
restaure usando root apenas nessa operação e mantenha a chave original do cofre:

```bash
dc stop frontend backend worker
dc exec -T db sh -c 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -h 127.0.0.1 -uroot "$MYSQL_DATABASE"' < backups/ARQUIVO_VALIDADO.sql
# Continue apenas se a importação terminou sem erro.
dc run --rm --no-deps init_db
# Continue apenas se init-db terminou com código zero.
dc up -d --no-build
```

## Atualização e recuperação

Após revisão e publicação manual das mudanças na branch `deploy/aws`:

1. Faça backup e registre a revisão atual com `git rev-parse HEAD`.
2. Com a árvore de trabalho limpa, execute `git pull --ff-only origin deploy/aws`.
3. Execute `dc config --quiet`, `dc build init_db` e `dc build frontend`.
4. Pare `frontend`, `backend` e `worker` durante a aplicação do esquema.
5. Execute `dc run --rm --no-deps init_db`; só prossiga se terminar com código zero.
6. Execute `dc up -d --no-build` e repita as verificações de saúde e navegação.

Há uma breve indisponibilidade nessa atualização. Não altere o nome do projeto,
não exclua o volume e não execute importadores antigos sobre bancos preenchidos.
Se houver falha, mantenha os dados, examine `dc logs` e retorne ao código/imagens
da revisão anterior em um checkout separado. Mudanças de esquema podem exigir
restaurar o backup; retornar apenas o código não desfaz alterações no banco.

## Validação local desta configuração — 10/11/2026

Verificações concluídas no Windows, sem acessar a AWS:

- Build Vite com `VITE_API_URL=/api`, Node 24 e heap de 512 MiB.
- Composição das URLs pelo Axios e inspeção do bundle: sem `/api/api` e sem
  `localhost:5000` no resultado compilado.
- `config --quiet` dos Composes de produção e desenvolvimento, usando o
  executável oficial portátil Docker Compose 5.7.0, com SHA-256 conferido.
- Configuração resolvida: somente frontend publica porta; banco permanece
  interno; volume nomeado e limites de memória presentes; segredos vazios são
  rejeitados. Regras de ignore verificadas para ambientes e chaves privadas.
- Instalação das dependências de produção em ambiente Python temporário isolado
  e `pip check`, sem incompatibilidades declaradas.
- Sintaxe Python e testes Flask de saúde, origem permitida/proibida e CORS com
  credenciais, sem consultar banco.
- Nginx 1.30.6 portátil com Flask real e React compilado: sintaxe, `/api/health`,
  query string, erros 404 da API, atualização direta de rotas React, origem 403 e
  limite de requisição 413. O teste adaptou apenas caminhos, usuário e endereços
  para Windows/loopback; as regras de proxy e roteamento foram preservadas.
- `git diff --check` e confirmação de que fontes da aplicação, regras de negócio,
  arquivos de desenvolvimento e referência `main` permaneceram inalterados.

**Pendências:** a máquina de revisão não tem Docker Engine nem WSL. Portanto,
não foram construídas/executadas as imagens Linux, nem iniciados MySQL, Gunicorn
ou worker em containers. A suíte de regressão que depende de MySQL, os fluxos
completos de pagamento/login/upload, persistência após reinício e uso real de RAM
precisam ser verificados em um ambiente Docker local ou CI antes da implantação.
O teste Flask usou Python 3.14; a imagem de produção usa Python 3.12 e Node 22
somente durante o build. Não houve teste de carga nem execução na AWS.

## Referências

- [Docker no Ubuntu e limites de firewall](https://docs.docker.com/engine/install/ubuntu/)
- [Compose em produção](https://docs.docker.com/compose/how-tos/production/)
- [Security Groups EC2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/security-group-rules-reference.html)
- [Flask em produção](https://flask.palletsprojects.com/en/stable/deploying/)
- [Variáveis do Vite no build](https://vite.dev/guide/env-and-mode)
- [Semântica de proxy_pass no Nginx](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_pass)
