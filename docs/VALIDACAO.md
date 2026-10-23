# Validação

```powershell
docker compose --profile testes run --build --rm testes
docker compose exec frontend npm run build
docker compose exec backend python -m compileall app
docker compose ps
```

O banco `ingressos_test` é independente e temporário (`tmpfs`). O fixture
recusa bancos cujo nome não termine em `_test` antes de limpar tabelas.
Depois de testar, `docker compose --profile testes stop db_test` libera recursos.

## Cobertura

- CRUD, buscas, filtros e relatório de categorias.
- Sessão, permissões, origem das mutações e bloqueio de elevação de papel.
- Cofre criptografado e revogação; exportação de dados apenas da própria conta.
- Datas, estoque, modalidade e centavos do comparador.
- Stored Procedure e duas compras simultâneas disputando estoque ou assento.
- Expiração, recusa, nova tentativa, aprovação idempotente e compra expressa atômica.
- Cancelamento e estorno simulados; bloqueio de código reutilizado.
- Documento privado, formato válido, análise e desconto após aprovação.
- Grupos, convites, participação e privacidade.
- Alertas, deduplicação, processamento e leitura.
- Recomendações locais por preferência.
- Relatório sem duplicação de valores e sem compras canceladas na receita.
- Proteção do histórico ao tentar excluir registros vinculados.

## Navegador

Uma conta fictícia entrou, escolheu lote/assento, criou a reserva e aprovou o
pagamento simulado. A carteira exibiu o ingresso com código único. Evidência:
`evidencias/carteira-demo.png`.

A verificação não representa homologação de gateway, autenticidade documental
externa ou certificação legal/de segurança.
