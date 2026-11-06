# Validação final — IngressoPlus

Data: 06/11/2026. Branch: `ajustes-rubrica`. Commit testado: `9499d55d283f1b52ece7c55c4cb9a533a76c7894`.

**Resultado: todos os cenários executados foram aprovados.** Nenhuma alteração no código-fonte foi necessária nesta rodada. Os números abaixo se referem a conjuntos que se sobrepõem e não devem ser somados como funcionalidades independentes.

| Conjunto | Resultado | Evidência |
|---|---|---|
| Suíte existente, MySQL real e isolado | **59/59**, 29,472 s | [resultado](evidencias/validacao-final-20261106145101/suite-resumo.txt) |
| Verificações adicionais da API | **51/51** | [requisições e conferências SQL](evidencias/validacao-final-20261106145101/api.json) |
| Fluxos pelo Chrome contra API/MySQL isolados | **31/31** | [resultados HTTP, interface e banco](evidencias/validacao-final-20261106145101/ui.json) |
| Responsividade, 16 combinações de tela/perfil × 4 larguras | **64/64** | [320, 375, 768 e 1440 px](evidencias/validacao-final-20261106145101/layout.json) |
| Modal de saída, 3 larguras | **3/3** | [cancelamento, Esc, foco, falha e confirmação](evidencias/validacao-final-20261106145101/modal-saida.json) |
| Partida e execução periódica do worker | **6/6** | [partida fria e dois ciclos reais](evidencias/validacao-final-20261106145101/worker.json) |
| Inicialização idempotente e importação com fixture | **2/2** | [validações por CLI](evidencias/validacao-final-20261106145101/operacional.json) |
| Fontes alternativas e foco por teclado | **APROVADO** | [fontes externas bloqueadas](evidencias/validacao-final-20261106145101/fallback-fontes.json) |
| Build Vite | **APROVADO**, 111 módulos, 4,39 s | [saída do build](evidencias/validacao-final-20261106145101/build-frontend.txt) |
| Configuração Docker Compose | **APROVADA** | `docker compose config --quiet` |

## Funcionalidades conferidas

- Cadastro, login, logout, papéis cliente/admin, rotas privadas, perfil e troca de senha.
- CRUD de usuários e eventos; buscas, filtros e datas com fuso.
- Campos acima dos limites retornando 400; limites exatos, acentos/emojis, descrição TEXT em bytes e opcionais preservados na suíte existente.
- Lotes, comparador, mapa, Stored Procedure, reserva, disponibilidade e concorrência de estoque/assento.
- Recusa/aprovação de pagamento simulado, idempotência, compra expressa, emissão, carteira, impressão, portaria, reuso, cancelamento e estorno.
- Upload/download de comprovante, rejeição motivada, aprovação, validade e meia-entrada.
- Cofre, consentimento/revogação, exportação, privacidade entre contas e histórico.
- Convites, participantes, totais e saída de grupos; agendamento, envio, leitura e cancelamento de alertas.
- Recomendações locais e relatórios por categoria/status e vendas.
- Nova agenda pública, tabela administrativa, filtros e navegação; títulos/textos removidos conforme solicitado.
- Logo, favicon SVG/ICO, título Ingresso+ e carregamento de Manrope/Space Grotesk.

As **49 combinações de rota/método** registradas no Flask tiveram pelo menos uma resposta 2xx no conjunto de API e navegador. Isso demonstra exercício dos endpoints, sem representar cobertura de todas as ramificações e entradas: [matriz de rotas](evidencias/validacao-final-20261106145101/rotas.json).

## Modal e interface

Foram conferidos: abrir sem efetuar logout; cancelar e pressionar Esc mantendo a sessão; confirmação enviando uma única requisição; bloqueio de cliques duplicados; estado Saindo; falha simulada mantendo a sessão; foco inicial/restauração e navegação por teclado. Cancelamento/confirmacão também foram executados com sessão real na API isolada.

Os testes de responsividade e de falhas do modal utilizaram respostas de API simuladas no navegador. Os 31 fluxos do conjunto de interface utilizaram API e MySQL reais e isolados, com consultas SQL para os casos de persistência. Não se atribui comprovação de backend aos testes apenas visuais.

Na primeira tentativa de perfil, o roteiro aguardava exclusivamente a URL /eventos; o login correto retornou à página /perfil que havia sido solicitada. O roteiro auxiliar foi ajustado à navegação válida e o caso foi reexecutado com sucesso. Nenhuma alteração da aplicação foi feita para resolver essa expectativa do roteiro. A tentativa inicial está preservada em [registro inicial](evidencias/validacao-final-20261106145101/ui-tentativa-inicial.json); o resultado consolidado está em ui.json.

## Worker e logs

O teste criou um MySQL separado inicialmente vazio. Uma falha intencional do inicializador (saída 23) bloqueou backend e worker. Na partida correta, init_db terminou com saída 0, as 13 tabelas e a Stored Procedure estavam presentes, e só então os dependentes iniciaram.

- Inicialização concluída: `2026-11-06T14:54:28.212239172Z`.
- Worker iniciado: `2026-11-06T14:54:28.898172492Z`.
- Dois ciclos independentes enviaram alertas e expiraram reservas, com observação por SQL, sem chamadas de API para processar as tarefas.
- Repetir init_db preservou os registros fictícios.
- Sem traceback, falha de tabela ausente ou HTTP 500 inesperado nos logs examinados. Respostas 400/401/403/404/409 dos testes negativos foram esperadas.

Evidências: [logs do ambiente de partida](evidencias/validacao-final-20261106145101/worker-logs.txt) e [inspeção de erros dos ambientes principal e isolado](evidencias/validacao-final-20261106145101/logs-erros.json).

## Preservação e encerramento

As operações de escrita e a suíte foram executadas em esquemas novos terminados em _test e em um MySQL temporário exclusivo para a partida fria. Nenhum volume ou banco preexistente foi removido, nenhuma credencial foi alterada e nenhum serviço principal foi reiniciado nesta rodada.

As contagens e checksums das **13 tabelas principais permaneceram iguais**. A API principal respondeu 200 em /api/health. Os serviços principais continuaram ativos, os bancos saudáveis e init_db com saída zero: [comparação antes/depois e serviços](evidencias/validacao-final-20261106145101/ambiente-principal.json).

Os serviços criados exclusivamente para esta validação foram parados ao término. Foram gerados apenas este documento e as evidências; sem commit, push ou merge.

## Comandos principais executados

```powershell
docker compose config --quiet
docker compose --profile testes run --build --rm --no-deps -e PYTHONDONTWRITEBYTECODE=1 -e DB_NAME=suite_final_20261106145101_test testes
docker compose exec -T frontend npm run build -- --outDir /tmp/ingressoplus-verificacao-final-build
```

O esquema de testes foi criado previamente com permissões do usuário de testes. --no-deps preservou o contêiner de testes preexistente; a suíte não utilizou o serviço backend ligado ao banco principal. O destino alternativo do build preservou os arquivos do host.

## Limites da conclusão

A aprovação vale para os cenários descritos. Pagamentos, estornos e canais do comparador são simulados conforme o escopo do projeto. Recomendações locais foram aprovadas; a chamada externa Gemini continua sem homologação por estar desativada/sem credencial. Impressora física, outros navegadores/dispositivos e carga prolongada não foram homologados nesta rodada.
