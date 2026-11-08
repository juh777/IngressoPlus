# Auditoria funcional — IngressoPlus

Data: 06/11/2026, 09:56:41 (America/Sao_Paulo). Branch: `ajustes-rubrica`. Commit: `2c5baabbf7b3201911e216fe73854a30271449a4`.

## Resultado

Os fluxos principais foram executados no navegador, na API e no MySQL. O sistema funciona para a demonstração acadêmica nos cenários válidos testados, mas há falhas reproduzíveis: campos maiores que o banco aceita retornam **HTTP 500**, e a busca automática do ícone do site retorna **404**.

| Inventário detalhado | Quantidade |
|---|---:|
| Itens funcionais e operacionais identificados | **57** |
| APROVADA | **54** |
| REPROVADA | **2** |
| NÃO TESTADA | **0** |
| DEPENDE DE CONFIGURAÇÃO | **1** |

Os 57 itens são o desdobramento dos recursos em operações e verificações auditáveis, incluindo CRUD anterior, segurança, ferramentas e interface. Não representam 57 grandes módulos. Dos **20 recursos documentados**, 19 passaram nos cenários cobertos; o recurso 13, gestão de eventos, possui a ressalva reprovada de limites de texto. O adaptador Gemini opcional depende de configuração e não impede as recomendações locais.

Validações executadas: **50/50 testes da suíte existente**, **51 verificações de API** (50 aprovadas e 1 reprovada), **31 verificações de navegador** (29 aprovadas e 2 reprovadas), 2 verificações operacionais e build de produção aprovado. Esses números se sobrepõem e não devem ser somados como funcionalidades diferentes. Todas as **49 combinações de rota/método da API** registradas no Flask receberam pelo menos uma resposta 2xx no conjunto dos roteiros; isso não equivale a cobertura integral de linhas, ramificações ou entradas.

## Ambiente e preservação dos dados

- Projeto auditado: `C:\Users\luca.castanheira\Desktop\IngressoPlus`.
- Ambiente principal: frontend em `localhost:5173`, API em `localhost:5000/api`, MySQL 8.4.13, backend/frontend/worker ativos e os dois MySQL saudáveis na inspeção.
- A interface principal abriu no Chrome e a API respondeu. As **13 tabelas principais estavam vazias antes e depois** da auditoria. As escritas de teste não usaram essa base. Não havia demonstração já carregada nela.
- Para a auditoria foram criados esquemas novos no contêiner de testes existente: `auditoria_20261106122743_test`, `suite_20261106122743_test` e `importacao_20261106122743_test`. O esquema preexistente de testes não foi limpo.
- API, frontend e worker temporários usaram o código atual, portas locais `15000/15173`, chave temporária própria e contas/arquivos fictícios. O backend foi montado somente para leitura. Os serviços principais não foram interrompidos.
- Nenhum arquivo de código-fonte, teste original, arquitetura, credencial de ambiente ou dado de demonstração existente foi alterado. Não houve commit, push, merge, remoção de contêiner, volume ou banco preexistente. Foram gerados este relatório e suas evidências.

Evidências: [serviços e versão](evidencias/auditoria-20261106122743/ambiente.json), [contagens finais da base principal](evidencias/auditoria-20261106122743/ambiente-principal-final.json), [interface principal inicial](evidencias/auditoria-20261106122743/ambiente-local-inicial.png) e [rotas exercitadas](evidencias/auditoria-20261106122743/cobertura-rotas.json).

## Método e interpretação

Foram lidos README, matriz de funcionalidades, documentação, fontes de frontend/backend, SQL de migrações, importador, testes e configuração Docker. Os roteiros da auditoria ficaram em diretório temporário, fora das fontes do projeto.

O navegador utilizado foi Chrome com Playwright, sessões separadas de administrador, dois clientes e visitante. As operações pela tela registraram método/URL/status HTTP; quando houve escrita, os resultados relevantes foram conferidos por consultas SQL independentes. Os JSON de evidência guardam verificações e resultados sem cookies, senhas ou códigos de ingresso/convite. As capturas de carteira e convite ocultam esses códigos.

As corridas de estoque/assento e a repetição de pagamento foram provocadas pela API; a seleção de assentos, ocupação, botões e atualização periódica foram verificadas no navegador. A ocupação de A2 foi atualizada em outra janela em cerca de **8,6 segundos**, sem recarregar.

O worker foi verificado aguardando alterações diretamente no banco, sem chamar as rotas que também processam vencimentos/avisos. Para expiração, apenas uma reserva fictícia recebeu prazo passado por SQL; o prazo original de quinze minutos foi conferido separadamente (899–900 segundos por precisão de armazenamento). Não se aguardaram quinze minutos reais.

Algumas tentativas iniciais do roteiro falharam por seletores de label, carga assíncrona de formulário, representação booleana JSON e documento com validade anterior ao evento. Foram reexecutadas com as precondições corretas; as evidências consolidadas identificam essas reverificações. Nenhuma correção do aplicativo foi aplicada para fazê-las passar.

## Cobertura dos 20 recursos documentados

| Item | Recurso | Resultado | Referências no inventário/evidências |
|---|---|---|---|
| 01 | Notificações de abertura | **APROVADA** | alerts.schedule, alerts.worker, alerts.read; UI alerts/alerts.event |
| 02 | Dados seguros | **APROVADA** | vault.consent; UI vault |
| 03 | Compra expressa | **APROVADA** | checkout.express; UI express |
| 04 | Monitoramento de lotes | **APROVADA** | lots.stock; UI polling, atualização sem reload |
| 05 | Comparador de taxas | **APROVADA** | fees.compare; UI reserve/half |
| 06 | Mapa interativo | **APROVADA** | seats.create, seats.availability; UI seats.create/seats.reserve |
| 07 | Grupos | **APROVADA** | groups.create/join/panel/leave; UI groups |
| 08 | Painel de ingressos | **APROVADA** | tickets.wallet; UI payments/print/gate |
| 09 | Regras de meia-entrada | **APROVADA** | documents.rules; UI documents.upload |
| 10 | Privacidade | **APROVADA** | privacy.export, vault.consent; UI export/vault |
| 11 | Autenticação | **APROVADA** | auth.*; UI register/login/access/fallback |
| 12 | Perfil | **APROVADA** | profile.update; UI profile |
| 13 | Gestão de eventos | **REPROVADA** | CRUD/lotes/mapa aprovados; validation.limits reprovada |
| 14 | Reservas | **APROVADA** | reservations.*; worker; UI reserve/seats.reserve/refund |
| 15 | Documento de meia | **APROVADA** | documents.upload/download/review; UI documents.* e half |
| 16 | Relatório de vendas | **APROVADA** | reports.sales; UI reports e SQL independente |
| 17 | Pagamento simulado | **APROVADA** | payments.refuse/approve/idempotency; UI payments/refund |
| 18 | Recomendações locais | **APROVADA** | recommendations.local; UI recommendations |
| 19 | Ocupação por Stored Procedure | **APROVADA** | seats.availability; UI seats.reserve/polling |
| 20 | Alertas por lote | **APROVADA** | alerts.lot/worker; UI alerts.event |

A aprovação é restrita ao comportamento entregue e aos cenários descritos: pagamentos/estornos e canais do comparador são simulados; alertas são internos; a recomendação padrão é local.

## Inventário detalhado de funcionalidades e verificações

Na coluna Evidência, o identificador corresponde ao campo `id` do JSON vinculado. `checks` contém as asserções, `http` as requisições observadas e `db` os resumos das consultas independentes. Itens sem ação de tela, como concorrência e execução do worker, não são apresentados como testes exclusivos de interface.

| Funcionalidade | Teste realizado | Resultado | Evidência | Observação |
|---|---|---|---|---|
| Saude HTTP, tabelas e Stored Procedure | GET health; conexão MySQL; 13 tabelas e Stored Procedure existentes. | **APROVADA** | [API: ambiente.health](evidencias/auditoria-20261106122743/api-consolidado.json); 1 conferência(s) de banco | Verificação de API/banco; não representa teste exclusivo da tela. |
| Criacao idempotente dos dados ficticios | Executar criar-demo duas vezes no esquema isolado e comparar contagens. | **APROVADA** | [API: cli.demo](evidencias/auditoria-20261106122743/api-consolidado.json); 1 conferência(s) de banco | Somente base nova; demonstração principal preservada. |
| Cadastro publico e papel de cliente | Cadastrar duas contas, tentar enviar papel admin, conferir hash e resposta. | **APROVADA** | [API: auth.register](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.register](evidencias/auditoria-20261106122743/ui-consolidado.json); [tela](evidencias/auditoria-20261106122743/ui-cadastro-concluido.png); 1 conferência(s) de banco | Interface + HTTP; persistência conferida nos casos com escrita. |
| Validacao de CPF, e-mail, senha e duplicidade | CPF inválido, e-mail inválido, senha curta e duplicidade. | **APROVADA** | [API: auth.validation](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.register](evidencias/auditoria-20261106122743/ui-consolidado.json); [tela](evidencias/auditoria-20261106122743/ui-cadastro-concluido.png) | Interface + HTTP; persistência conferida nos casos com escrita. |
| Login, senha incorreta e sessao | Senha incorreta 401, senha correta 200, sessão e registro de ação. | **APROVADA** | [API: auth.login](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.login](evidencias/auditoria-20261106122743/ui-consolidado.json); [tela](evidencias/auditoria-20261106122743/ui-permissao-cliente.png); 1 conferência(s) de banco | Interface + HTTP; persistência conferida nos casos com escrita. |
| Logout encerra sessao | Logout 204 e acesso subsequente à sessão 401. | **APROVADA** | [API: auth.logout](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.fallback](evidencias/auditoria-20261106122743/ui-consolidado.json) | Interface + HTTP; persistência conferida nos casos com escrita. |
| Permissoes administrativas e rotas privadas | Anônimo e cliente nas rotas privadas/admin; tentativa de elevação de papel. | **APROVADA** | [API: auth.permissions](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.access, ui.login](evidencias/auditoria-20261106122743/ui-consolidado.json); [tela](evidencias/auditoria-20261106122743/ui-eventos-publicos.png) | Interface + HTTP; persistência conferida nos casos com escrita. |
| Protecao de origem e CORS | Origem permitida com credenciais; mutação com origem estranha 403. | **APROVADA** | [API: guard.origin](evidencias/auditoria-20261106122743/api-consolidado.json) | Verificação HTTP; não depende de ação de tela. |
| CRUD administrativo de usuarios | Criar, consultar, editar e excluir; conferir mudança e ausência no MySQL. | **APROVADA** | [API: users.crud](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.users](evidencias/auditoria-20261106122743/ui-consolidado.json); [tela](evidencias/auditoria-20261106122743/ui-crud-usuarios.png); 1 conferência(s) de banco | Fluxo válido aprovado; nome acima do limite também reproduz HTTP 500. |
| Busca administrativa e entrada SQL como texto | Buscar e-mail, busca sem distinção de caixa, termo SQL literal e termo vazio. | **APROVADA** | [API: users.search](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.users](evidencias/auditoria-20261106122743/ui-consolidado.json); [tela](evidencias/auditoria-20261106122743/ui-crud-usuarios.png) | Interface + HTTP; persistência conferida nos casos com escrita. |
| Reverificacao de perfil e senha | Editar telefone/nome/senha; papel permanece cliente; senha antiga recusada e nova aceita. | **APROVADA** | [API: profile.update](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.profile](evidencias/auditoria-20261106122743/ui-consolidado.json); 1 conferência(s) de banco | Interface + HTTP; persistência conferida nos casos com escrita. |
| Cadastro de eventos e validacao de cronograma | Criar evento válido; rejeitar abertura posterior ao evento; conferir MySQL. | **APROVADA** | [API: events.create](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.events](evidencias/auditoria-20261106122743/ui-consolidado.json); [tela](evidencias/auditoria-20261106122743/ui-eventos-admin.png); 1 conferência(s) de banco | Fluxo válido aprovado; limites de texto tratados separadamente na reprovação validation.limits. |
| Listagem e consulta publica de eventos | Listar, abrir detalhes e solicitar ID inexistente. | **APROVADA** | [API: events.list](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.access, ui.events](evidencias/auditoria-20261106122743/ui-consolidado.json); [tela](evidencias/auditoria-20261106122743/ui-eventos-publicos.png) | Interface + HTTP; persistência conferida nos casos com escrita. |
| Edicao de evento e conversao de fuso | Editar descrição e converter 20h -03:00 para 23h UTC no banco. | **APROVADA** | [API: events.update](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.events.edit](evidencias/auditoria-20261106122743/ui-consolidado.json); [tela](evidencias/auditoria-20261106122743/ui-filtros-eventos.png); 1 conferência(s) de banco | Interface + HTTP; persistência conferida nos casos com escrita. |
| Exclusao de evento sem vinculos | Excluir evento descartável sem vínculos; HTTP 204 e linha ausente. | **APROVADA** | [API: events.delete](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.events.edit](evidencias/auditoria-20261106122743/ui-consolidado.json); [tela](evidencias/auditoria-20261106122743/ui-filtros-eventos.png); 1 conferência(s) de banco | Interface + HTTP; persistência conferida nos casos com escrita. |
| Filtros de categoria, local e situacao | Combinar categoria/local/status; situação inválida e texto SQL literal. | **APROVADA** | [API: events.filter](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.events.edit](evidencias/auditoria-20261106122743/ui-consolidado.json); [tela](evidencias/auditoria-20261106122743/ui-filtros-eventos.png) | Interface + HTTP; persistência conferida nos casos com escrita. |
| Gestao de lotes e validacao de valores | Criar lote de 100,00, 30 unidades, taxa 10%; preços inválidos e período futuro. | **APROVADA** | [API: lots.create](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.lots](evidencias/auditoria-20261106122743/ui-consolidado.json); [tela](evidencias/auditoria-20261106122743/ui-gestao-lotes.png); 1 conferência(s) de banco | Interface + HTTP; persistência conferida nos casos com escrita. |
| Comparador simulado de taxas e modalidade | Duas meias: subtotal 100,00, taxa 10,00, total 110,00; ordenação; entradas inválidas. | **APROVADA** | [API: fees.compare](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.reserve, ui.half](evidencias/auditoria-20261106122743/ui-consolidado.json); [tela](evidencias/auditoria-20261106122743/ui-reserva.png) | Interface + HTTP; persistência conferida nos casos com escrita. |
| Criacao de mapa de assentos | Criar 2 filas × 3 lugares; banco com 6 assentos; segunda criação recusada. | **APROVADA** | [API: seats.create](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.seats.create](evidencias/auditoria-20261106122743/ui-consolidado.json); [tela](evidencias/auditoria-20261106122743/ui-mapa-criado.png); 1 conferência(s) de banco | Interface + HTTP; persistência conferida nos casos com escrita. |
| Reverificacao do prazo de reserva | Reservar 3 unidades por 330,00, conferir prazo e rejeitar quantidade excessiva. | **APROVADA** | [API: reservations.create](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.reserve](evidencias/auditoria-20261106122743/ui-consolidado.json); [tela](evidencias/auditoria-20261106122743/ui-reserva.png); 1 conferência(s) de banco | Interface + HTTP; persistência conferida nos casos com escrita. |
| Disponibilidade considera reservas e rejeita excesso | Disponibilidade desconta reservas; duas requisições simultâneas disputam a última unidade. | **APROVADA** | [API: lots.stock](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.polling, ui.seats.reserve](evidencias/auditoria-20261106122743/ui-consolidado.json); [tela](evidencias/auditoria-20261106122743/ui-atualizacao-automatica.png); 1 conferência(s) de banco | Corrida na API: uma reserva e um conflito. Segunda janela atualizou A2 em 8,6 s sem reload. |
| Reservas e pagamentos privados entre contas | Outra conta tenta pagar/cancelar reserva alheia e recebe 404. | **APROVADA** | [API: reservations.ownership](evidencias/auditoria-20261106122743/api-consolidado.json) | Verificação de API/banco; não representa teste exclusivo da tela. |
| Recusa simulada sem emissao e nova tentativa | Recusa não emite ingresso e mantém reserva disponível para nova tentativa. | **APROVADA** | [API: payments.refuse](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.payments](evidencias/auditoria-20261106122743/ui-consolidado.json); [tela](evidencias/auditoria-20261106122743/ui-pagamento-carteira.png); 1 conferência(s) de banco | Interface + HTTP; persistência conferida nos casos com escrita. |
| Pagamento simulado aprovado e emissao | Aprovação gera 1 pagamento e 3 ingressos com códigos distintos. | **APROVADA** | [API: payments.approve](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.payments](evidencias/auditoria-20261106122743/ui-consolidado.json); [tela](evidencias/auditoria-20261106122743/ui-pagamento-carteira.png); 1 conferência(s) de banco | Interface + HTTP; persistência conferida nos casos com escrita. |
| Pagamento repetido nao duplica cobranca ou ingressos | Repetir aprovação preserva pagamento único e quantidade de ingressos. | **APROVADA** | [API: payments.idempotency](evidencias/auditoria-20261106122743/api-consolidado.json); 1 conferência(s) de banco | Requisição repetida testada pela API; tela remove botões de pagar após aprovação. |
| Carteira e listagem de reservas | Carteira e reservas próprias; três ingressos renderizados na API e emissão na tela. | **APROVADA** | [API: tickets.wallet](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.payments](evidencias/auditoria-20261106122743/ui-consolidado.json); [tela](evidencias/auditoria-20261106122743/ui-pagamento-carteira.png) | Interface + HTTP; persistência conferida nos casos com escrita. |
| Relatorio de vendas por evento e lote | Compra de 3 ingressos: receita 330,00 e taxa 30,00; conferência independente no MySQL. | **APROVADA** | [API: reports.sales](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.reports](evidencias/auditoria-20261106122743/ui-consolidado.json); [tela](evidencias/auditoria-20261106122743/ui-relatorio-eventos.png); 1 conferência(s) de banco | Interface + HTTP; persistência conferida nos casos com escrita. |
| Cancelamento, estorno e liberacao do estoque | Cancelar compra paga; estorno persistido; ingresso inválido; receita removida. | **APROVADA** | [API: reservations.cancel](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.refund](evidencias/auditoria-20261106122743/ui-consolidado.json); [tela](evidencias/auditoria-20261106122743/ui-estorno.png); 1 conferência(s) de banco | Interface + HTTP; persistência conferida nos casos com escrita. |
| Compra expressa atomica | Exigir confirmação; reserva/pagamento/ingresso persistidos juntos. | **APROVADA** | [API: checkout.express](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.express](evidencias/auditoria-20261106122743/ui-consolidado.json); [tela](evidencias/auditoria-20261106122743/ui-expressa.png); 1 conferência(s) de banco | Interface + HTTP; persistência conferida nos casos com escrita. |
| Reverificacao de uso na portaria | Validar código uma vez; reuso 409; cancelamento após utilização 409. | **APROVADA** | [API: tickets.validate](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.gate](evidencias/auditoria-20261106122743/ui-consolidado.json); [tela](evidencias/auditoria-20261106122743/ui-portaria-reuso.png); 1 conferência(s) de banco | Interface + HTTP; persistência conferida nos casos com escrita. |
| Mapa, Stored Procedure e disputa de assento | Exigir assento e quantidade 1; disputa simultânea 201/409; procedure ocupada; cancelar libera. | **APROVADA** | [API: seats.availability](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.seats.reserve, ui.polling](evidencias/auditoria-20261106122743/ui-consolidado.json); [tela](evidencias/auditoria-20261106122743/ui-assento-ocupado.png); 1 conferência(s) de banco | Interface + HTTP; persistência conferida nos casos com escrita. |
| Worker expira reserva sem consulta da API | Antecipar expira_em somente na fixture; aguardar worker sem chamar API de reservas; pagar expirado 409. | **APROVADA** | [API: reservations.expiration](evidencias/auditoria-20261106122743/api-consolidado.json); 1 conferência(s) de banco | Sem aguardar 15 min reais: prazo 899–900 s conferido e vencimento antecipado só na fixture. Worker real executou a expiração. |
| Regras publicas de meia-entrada | GET público retorna 4 categorias e desconto de 50%; regras também conferidas na central autenticada. | **APROVADA** | [API: documents.rules](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.documents.upload](evidencias/auditoria-20261106122743/ui-consolidado.json); [tela](evidencias/auditoria-20261106122743/ui-documento-pendente.png) | API pública; página de meia-entrada exige login conforme roteamento atual. |
| Upload privado com validacao de formato tamanho e validade | Formato inválido, arquivo >2 MB, validade passada e upload válido pendente. | **APROVADA** | [API: documents.upload](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.documents.upload](evidencias/auditoria-20261106122743/ui-consolidado.json); [tela](evidencias/auditoria-20261106122743/ui-documento-pendente.png); 1 conferência(s) de banco | Arquivos fictícios; teste não homologa autenticidade documental. |
| Download do comprovante e privacidade | Titular e admin recebem PDF; terceiro recebe 404; download real no navegador. | **APROVADA** | [API: documents.download](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.documents.download](evidencias/auditoria-20261106122743/ui-consolidado.json) | Interface + HTTP; persistência conferida nos casos com escrita. |
| Documento valido na data do evento permite meia-entrada | Rejeição exige motivo; decisão exibida; aprovação válida no evento libera meia por 55,00. | **APROVADA** | [API: documents.review](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.documents.review, ui.half](evidencias/auditoria-20261106122743/ui-consolidado.json); [tela](evidencias/auditoria-20261106122743/ui-analise-documento.png); 2 conferência(s) de banco | Documento que vence antes do evento foi corretamente recusado; novo documento válido até 2028 liberou desconto. |
| Consentimento, criptografia e revogacao | Aceitar, salvar, ler e revogar; conteúdo criptografado no MySQL e remoção após revogação. | **APROVADA** | [API: vault.consent](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.vault](evidencias/auditoria-20261106122743/ui-consolidado.json); [tela](evidencias/auditoria-20261106122743/ui-privacidade.png); 2 conferência(s) de banco | Interface + HTTP; persistência conferida nos casos com escrita. |
| Exportacao e isolamento dos dados pessoais | Baixar JSON real; conferir perfil/reservas próprios, ausência de hash e registro de exportação. | **APROVADA** | [API: privacy.export](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.export](evidencias/auditoria-20261106122743/ui-consolidado.json); [tela](evidencias/auditoria-20261106122743/ui-exportacao.png); 1 conferência(s) de banco | Interface + HTTP; persistência conferida nos casos com escrita. |
| Criacao de grupo e participante criador | Criar grupo, incluir criador e conferir persistência. | **APROVADA** | [API: groups.create](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.groups](evidencias/auditoria-20261106122743/ui-consolidado.json); [tela](evidencias/auditoria-20261106122743/ui-grupo-painel.png); 1 conferência(s) de banco | Interface + HTTP; persistência conferida nos casos com escrita. |
| Convite, duplicidade de participacao e privacidade | Terceiro sem convite 404; código inexistente 404; convite repetido não duplica membro. | **APROVADA** | [API: groups.join](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.groups](evidencias/auditoria-20261106122743/ui-consolidado.json); [tela](evidencias/auditoria-20261106122743/ui-grupo-painel.png); 1 conferência(s) de banco | Interface + HTTP; persistência conferida nos casos com escrita. |
| Painel do grupo e totais individuais | Participantes veem painel; total considera compras pagas e exclui canceladas. | **APROVADA** | [API: groups.panel](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.groups](evidencias/auditoria-20261106122743/ui-consolidado.json); [tela](evidencias/auditoria-20261106122743/ui-grupo-painel.png); 1 conferência(s) de banco | Interface + HTTP; persistência conferida nos casos com escrita. |
| Saida do grupo e protecao do criador | Criador não pode sair; participante sai e perde acesso ao painel. | **APROVADA** | [API: groups.leave](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.groups](evidencias/auditoria-20261106122743/ui-consolidado.json); [tela](evidencias/auditoria-20261106122743/ui-grupo-painel.png) | Interface + HTTP; persistência conferida nos casos com escrita. |
| Agendamento personalizado e duplicidade | Data personalizada e tentativa duplicada; conferir agendamento no banco. | **APROVADA** | [API: alerts.schedule](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.alerts](evidencias/auditoria-20261106122743/ui-consolidado.json); [tela](evidencias/auditoria-20261106122743/ui-alerta-cancelado.png); 1 conferência(s) de banco | Interface + HTTP; persistência conferida nos casos com escrita. |
| Cancelar alerta proprio e impedir alteracao alheia | Cancelamento próprio persistido; outra conta não altera o aviso. | **APROVADA** | [API: alerts.cancel](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.alerts](evidencias/auditoria-20261106122743/ui-consolidado.json); [tela](evidencias/auditoria-20261106122743/ui-alerta-cancelado.png); 1 conferência(s) de banco | Interface + HTTP; persistência conferida nos casos com escrita. |
| Alertas de abertura geral e de lote | Alerta vinculado ao lote; lote de outro evento rejeitado; botão do evento exercitado. | **APROVADA** | [API: alerts.lot](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.alerts.event](evidencias/auditoria-20261106122743/ui-consolidado.json); [tela](evidencias/auditoria-20261106122743/ui-alertas-enviados.png); 1 conferência(s) de banco | Interface + HTTP; persistência conferida nos casos com escrita. |
| Worker entrega alerta sem pagina ou GET de alertas | Aviso vence e muda para enviado no banco sem página aberta nem GET de alertas. | **APROVADA** | [API: alerts.worker](evidencias/auditoria-20261106122743/api-consolidado.json); 1 conferência(s) de banco | Polling somente via SQL, sem a API que também pode processar avisos. |
| Listagem e leitura de notificacao | Listar aviso enviado, marcar como lido e conferir lido=1 no MySQL. | **APROVADA** | [API: alerts.read](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.alerts.event](evidencias/auditoria-20261106122743/ui-consolidado.json); [tela](evidencias/auditoria-20261106122743/ui-alertas-enviados.png); 1 conferência(s) de banco | Interface + HTTP; persistência conferida nos casos com escrita. |
| Recomendacoes por preferencias e historico | Salvar preferência consentida; API pontua categoria; recomendações aparecem na interface. | **APROVADA** | [API: recommendations.local](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.recommendations](evidencias/auditoria-20261106122743/ui-consolidado.json); [tela](evidencias/auditoria-20261106122743/ui-recomendacoes.png) | Motor local aprovado; chamada externa Gemini avaliada em item separado. |
| Relatorio agregado por categoria e situacao | Comparar totais/categorias/status com SQL independente e métricas da tela. | **APROVADA** | [API: reports.events](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.reports](evidencias/auditoria-20261106122743/ui-consolidado.json); [tela](evidencias/auditoria-20261106122743/ui-relatorio-eventos.png); 1 conferência(s) de banco | Interface + HTTP; persistência conferida nos casos com escrita. |
| Historico impede exclusao de registros vinculados | Tentar excluir evento/usuário com vendas; HTTP 409 preserva histórico. | **APROVADA** | [API: integrity.history](evidencias/auditoria-20261106122743/api-consolidado.json) | Verificação de API/banco; não representa teste exclusivo da tela. |
| Validacao dos limites de texto sem HTTP 500 | Enviar nome de 151 caracteres pelo formulário/API; testar local 201, categoria 81, imagem 301 e nome de usuário 151. | **REPROVADA** | [API: validation.limits](evidencias/auditoria-20261106122743/api-consolidado.json); [UI: ui.limits](evidencias/auditoria-20261106122743/ui-consolidado.json); [tela](evidencias/auditoria-20261106122743/ui-erro-limite-nome.png); 1 conferência(s) de banco | REPRODUZÍVEL: HTTP 500 e mensagem genérica; nenhum registro inválido persistiu. Ver problema P1. |
| Inicializacao do esquema preserva registros existentes | Reexecutar flask init-db no esquema auditado e comparar contagens. | **APROVADA** | [schema.idempotent](evidencias/auditoria-20261106122743/operacional.json) | Operação técnica via CLI; sem dados reais. |
| Importador de JSON legado com fixture ficticia e rollback | Importar fixture JSON em outro esquema vazio; comparar campos/IDs/hash; recusar repetição em banco ocupado. | **APROVADA** | [migration.import](evidencias/auditoria-20261106122743/operacional.json) | Operação técnica via CLI; sem dados reais. |
| Impressao da carteira | Acionar botão, confirmar chamada window.print e CSS de impressão com ingresso visível. | **APROVADA** | [ui.print](evidencias/auditoria-20261106122743/ui-consolidado.json); [tela](evidencias/auditoria-20261106122743/ui-carteira-impressao.png) | Diálogo físico/impressora não testados; chamada e estilo de impressão verificados. |
| Rotas inexistentes, evento ausente e logout | Abrir URL inexistente, evento ausente e rota privada após sair. | **APROVADA** | [ui.fallback](evidencias/auditoria-20261106122743/ui-consolidado.json) | Erros apresentados e redirecionamento de sessão confirmados. |
| Console e navegacao das paginas autenticadas | Navegar pelas páginas autenticadas; capturar console, exceções JavaScript e origem do recurso ausente. | **REPROVADA** | [ui.console](evidencias/auditoria-20261106122743/ui-consolidado.json) | Somente favicon.ico 404; zero exceções JavaScript. Ver P2. |
| Adaptador Gemini opcional | Inspeção da configuração atual: integração desativada e chave ausente. | **DEPENDE DE CONFIGURAÇÃO** | [ambiente](evidencias/auditoria-20261106122743/ambiente.json); backend/app/services/recomendacao_service.py | Chamada real não executada; retorno local funciona. Não integra os 20 recursos como requisito de serviço externo. |

## Problemas por gravidade e correções sugeridas

### P1 — MÉDIA: ausência de limites de texto produz HTTP 500

**Reprodução:** entrar como administrador; abrir Novo Evento; informar nome com 151 caracteres, local válido e datas válidas; salvar. A tela exibe `Nao foi possivel cadastrar o evento` e `POST /api/eventos` retorna 500. O comportamento ocorreu tanto pela API quanto pelo formulário. A linha inválida não foi gravada.

Também foram reproduzidos HTTP 500 para:

| Recurso/campo | Limite da coluna | Tamanho enviado |
|---|---:|---:|
| Evento: nome | 150 | 151 |
| Evento: local | 200 | 201 |
| Evento: categoria | 80 | 81 |
| Evento: imagem_url | 300 | 301 |
| Usuário: nome | 150 | 151 |

**Esperado:** recusar a entrada com erro de validação 400 e mensagem do campo. O banco limita os tamanhos, mas a validação anterior ao ORM não faz essa conferência; as exceções SQLAlchemy são convertidas em erro genérico 500. A tela de eventos não tem `maxLength` nesses campos.

**Arquivos relacionados:** [validators.py](../backend/app/utils/validators.py), [criar_evento_service.py](../backend/app/services/eventos/criar_evento_service.py), [atualizar_evento_service.py](../backend/app/services/eventos/atualizar_evento_service.py), [criar_usuario_service.py](../backend/app/services/usuarios/criar_usuario_service.py), [atualizar_usuario_service.py](../backend/app/services/usuarios/atualizar_usuario_service.py), [Evento](../backend/app/models/evento.py), [Usuario](../backend/app/models/usuario.py), [EventoForm.jsx](../frontend/src/pages/Eventos/EventoForm.jsx), [UsuarioForm.jsx](../frontend/src/pages/Usuarios/UsuarioForm.jsx) e [Perfil.jsx](../frontend/src/pages/Conta/Perfil.jsx).

**Correção mínima sugerida:** validar os comprimentos correspondentes às colunas antes de salvar, reaproveitando os validadores existentes; incluir limites nos inputs apropriados; acrescentar regressão de entrada longa e conferir que uma operação válida continua funcionando após a recusa. A edição compartilha a ausência de limites observada no código, mas o teste de tamanho excedente reproduzido nesta auditoria usou criação; não se afirma execução de todos os campos em todas as telas.

Evidências: [matriz adicional](evidencias/auditoria-20261106122743/limites-adicionais.json), [validation.limits](evidencias/auditoria-20261106122743/api-consolidado.json), [erro visível no formulário](evidencias/auditoria-20261106122743/ui-erro-limite-nome.png) e [HTTP 500 nos logs](evidencias/auditoria-20261106122743/logs-resumo.txt).

### P2 — BAIXA: ícone ausente gera erro 404 no console

**Reprodução:** abrir a aplicação em uma sessão nova do Chrome e navegar pelas páginas. A requisição automática `GET /favicon.ico` em `localhost:15173` retorna 404; a origem foi registrada no console. As requisições válidas da API nessa navegação retornaram 200 e não houve exceção JavaScript.

**Impacto:** ruído no console e ausência de ícone da aba; os fluxos de negócio testados continuam operantes.

**Arquivo relacionado:** [frontend/index.html](../frontend/index.html), sem definição de ícone, e recurso ausente em `frontend/public/favicon.ico`.

**Correção mínima sugerida:** definir um ícone válido no HTML ou disponibilizar o favicon estático correspondente.

Evidência: [ui.console; origem favicon.ico](evidencias/auditoria-20261106122743/ui-consolidado.json).

### Observação operacional — BAIXA: worker inicia antes da criação das tabelas

O log do worker principal contém um erro histórico em **06/11/2026 11:25:52 UTC**: tabela `ingressos_db.alertas` inexistente. O Compose aguarda o backend iniciar, mas não aguarda `flask init-db` terminar. O worker registra a falha e tenta novamente a cada dez segundos. Não foi necessário reiniciá-lo e não houve repetição recente desse erro na inspeção; o worker isolado comprovou processamento de aviso e expiração.

**Arquivos relacionados:** [docker-compose.yml](../docker-compose.yml), [Dockerfile](../backend/Dockerfile), [worker.py](../backend/worker.py).

**Sugestão:** fazer a dependência do worker aguardar a prontidão do esquema/backend. Não é uma reprovação do processamento periódico demonstrado; o erro inicial do ambiente principal não foi reproduzido desligando serviços existentes.

Evidência: [erro histórico e logs da auditoria](evidencias/auditoria-20261106122743/logs-resumo.txt).

**Atualização de 06/11/2026 — inicialização do worker corrigida:** a criação do
esquema foi movida para o serviço `init_db`. Backend e worker dependem de
`service_completed_successfully`; o Dockerfile do backend inicia somente a API.
O ciclo de dez segundos e o tratamento de falhas do worker foram preservados.

A validação usou um MySQL isolado inicialmente vazio: uma falha simulada de
`init_db` (saída 23) bloqueou os dois dependentes; com a inicialização correta,
as 13 tabelas e a Stored Procedure ficaram prontas antes de ambos iniciarem.
Dois ciclos reais enviaram alertas e expiraram reservas sem chamadas de API.
Repetir `init_db` preservou os registros de teste. Os 59 testes existentes
passaram em 41,411 segundos.

A correção foi aplicada ao Docker local: `init_db` terminou às
13:56:05.078 UTC e o worker iniciou às 13:56:05.502 UTC, sem a falha inicial.
Backend e banco principal permaneceram operantes. As 12 tabelas fora de
`auditoria` mantiveram contagens e checksums; somente um novo registro normal
de login foi acrescentado ao histórico durante o uso do site. Nenhum dado
existente foi apagado ou recriado.

Evidências posteriores: [testes de inicialização](evidencias/worker-inicializacao-20261106135339/testes-inicializacao.json),
[serviços e preservação dos dados](evidencias/worker-inicializacao-20261106135339/validacao-principal.json),
[logs da partida isolada](evidencias/worker-inicializacao-20261106135339/logs-ambiente-isolado.txt),
[logs locais após a correção](evidencias/worker-inicializacao-20261106135339/logs-ambiente-principal.txt)
e [resultado da suíte](evidencias/worker-inicializacao-20261106135339/suite-resumo.txt).

## Suíte automatizada e build executados

As imagens foram reconstruídas antes dos testes. Para não recriar o contêiner de testes que já existia e para não limpar sua base preexistente, a execução usou `--no-deps` e um esquema novo terminado em `_test`:

```powershell
docker compose --profile testes build testes frontend
docker compose --profile testes run --rm --no-deps -e PYTHONDONTWRITEBYTECODE=1 -e DB_NAME=suite_20261106122743_test testes
docker compose exec -T frontend npm run build -- --outDir /tmp/ingressoplus-auditoria-build
```

- Suíte: **Ran 50 tests in 34.695s — OK**, saída 0. Executou contra o MySQL de testes, com dados isolados. Nenhuma asserção original foi removida ou enfraquecida.
- Build: **111 módulos transformados**, concluído em **8,33 s**, saída 0. O diretório alternativo dentro do contêiner preservou os arquivos do host. O aviso de saída fora da raiz foi esperado para esse destino.
- O build valida a compilação; os testes Chrome descritos acima validam o uso da interface em modo Vite, não uma implantação de produção com servidor estático.

Saídas registradas: [trecho final da suíte com resumo completo](evidencias/auditoria-20261106122743/suite-50-testes.txt) e [resumo do build](evidencias/auditoria-20261106122743/build-frontend.txt).

## Limites e pendências de configuração

1. **Gemini real:** DEPENDE DE CONFIGURAÇÃO. `USAR_GEMINI` estava desativado e a chave ausente. Não foi ativado serviço externo nem consumida API paga; não se homologa a chamada real nem sua resposta. Preferências e histórico locais foram testados.
2. **Impressão:** botão, chamada de impressão e CSS conferidos no Chrome; impressão física e drivers não foram testados.
3. **Importação:** fixture sintética validou o importador e a recusa em banco ocupado; não havia backup PostgreSQL real fornecido para homologar uma migração de produção.
4. **Dados e temporização:** dados fictícios; prazos de expiração antecipados apenas no esquema isolado, sem aguardar quinze minutos reais. Não foi realizado teste prolongado de carga/disponibilidade.
5. **Navegadores/dispositivos:** Chrome desktop automatizado; não houve homologação separada em Safari, Firefox ou aparelhos móveis, nem auditoria completa de acessibilidade.
6. **Escopo implementado:** gateway real, pagamentos reais, validação documental externa, e-mail/SMS/push e certificações legais não existem no escopo declarado. Não foram classificados como defeitos de funcionalidades implementadas.
7. **Segurança:** papéis, privacidade entre contas, hash, cofre, origem, injeção SQL como texto e concorrência foram exercitados. Isso não constitui garantia de ausência de vulnerabilidades ou teste de invasão completo.

O valor zero em NÃO TESTADA refere-se aos itens do inventário principal para os quais foi definido teste executável; os cenários complementares acima permanecem fora da cobertura e não são declarados aprovados. O único adaptador implementado cuja chamada real ficou pendente aparece como DEPENDE DE CONFIGURAÇÃO.

## Prontidão para apresentação escolar

**Pronto para demonstrar os fluxos válidos cobertos, com as ressalvas P1/P2 e preparação de dados. Não é correto declarar funcionamento 100% sem ressalvas.** Reserva, pagamento simulado, meia, assentos, estorno, portaria, grupos, alertas, recomendações locais e relatórios funcionaram com interface e persistência conferidas.

O banco principal estava vazio. Antes de apresentar, é necessário preparar contas/eventos/lotes de demonstração e ensaiar o roteiro. A auditoria não executou `criar-demo` no banco principal; confirmou a ferramenta somente no ambiente isolado. A criação de demonstração deve ser uma decisão de preparação separada, não uma suposta correção automática deste relatório.

Prioridades sugeridas: corrigir validação dos comprimentos; opcionalmente corrigir favicon e prontidão de inicialização do worker; depois repetir os testes afetados. As correções aguardam autorização do usuário.

## Artefatos e encerramento

- [51 verificações de API](evidencias/auditoria-20261106122743/api-consolidado.json).
- [31 verificações Chrome, HTTP e SQL](evidencias/auditoria-20261106122743/ui-consolidado.json).
- [inicialização e importação](evidencias/auditoria-20261106122743/operacional.json).
- [reproduções adicionais do HTTP 500](evidencias/auditoria-20261106122743/limites-adicionais.json).
- [49 combinações de rota/método com resposta 2xx](evidencias/auditoria-20261106122743/cobertura-rotas.json).
- [erros relevantes dos logs](evidencias/auditoria-20261106122743/logs-resumo.txt).
- [banco principal preservado](evidencias/auditoria-20261106122743/ambiente-principal-final.json).
- [carteira](evidencias/auditoria-20261106122743/ui-pagamento-carteira.png), [assento ocupado](evidencias/auditoria-20261106122743/ui-assento-ocupado.png), [atualização entre janelas](evidencias/auditoria-20261106122743/ui-atualizacao-automatica.png), [grupo](evidencias/auditoria-20261106122743/ui-grupo-painel.png), [alertas](evidencias/auditoria-20261106122743/ui-alertas-enviados.png), [relatório de vendas](evidencias/auditoria-20261106122743/ui-relatorio-vendas.png).

Os serviços temporários exclusivos desta auditoria foram parados ao concluir, preservando seus contêineres e esquemas. Os serviços e bancos preexistentes permaneceram ativos e não foram removidos. A contagem final do banco principal permaneceu zero nas 13 tabelas. Nenhuma correção de aplicação foi executada.
