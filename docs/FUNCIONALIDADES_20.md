# Matriz de implementação

As dez ampliações abaixo cobrem os vinte itens do documento de referência,
preservando o CRUD anterior. A contagem dos recursos do PDF agrupa operações
de forma diferente da contagem do CRUD.

| Módulo acrescentado | Itens do documento | Interface | API principal |
|---|---|---|---|
| 1. Contas e acesso | 11, 12 | Login, cadastro e perfil | `/auth/*`, `/perfil` |
| 2. Cofre e privacidade | 2, 10 | Perfil: consentimento e exportação | `/perfil/cofre`, `/perfil/exportar` |
| 3. Lotes e taxas | 4, 5, 13 | Estoque e comparador no evento | `/eventos/{id}/lotes`, `/lotes/{id}/taxas` |
| 4. Assentos e ocupação | 6, 19 | Mapa numerado | `/eventos/{id}/assentos` |
| 5. Reservas | 14 | Evento e carteira | `/reservas`, `/reservas/{id}/cancelar` |
| 6. Checkout e expressa | 3, 17 | Carteira e compra em um clique | `/reservas/{id}/pagamento`, `/checkout/expressa` |
| 7. Carteira e portaria | 8 | Meus ingressos e validação admin | `/ingressos`, `/ingressos/validar` |
| 8. Meia-entrada | 9, 15 | Central e análise de documentos | `/meia/regras`, `/meia/documentos` |
| 9. Grupos | 7 | Convite e participantes | `/grupos`, `/grupos/entrar` |
| 10. Alertas, descoberta e métricas | 1, 16, 18, 20 | Alertas, recomendações e vendas | `/alertas`, `/recomendacoes`, `/relatorios/vendas/{id}` |

## Fluxo integrado

O servidor bloqueia o lote e o assento envolvidos e verifica estoque, período,
modalidade e documento. A reserva fixa preço e taxa por quinze minutos.
A aprovação simulada gera um pagamento por reserva e um ingresso por unidade.
Repetir a aprovação retorna o resultado existente. A compra expressa executa
reserva e aprovação na mesma transação; qualquer falha desfaz tudo.

O cancelamento libera estoque/assento e, em compra paga, registra estorno
simulado e invalida o código. Depois da utilização ou início do evento,
o cancelamento é recusado. O relatório considera somente compras pagas e
não multiplica a arrecadação pelo número de ingressos.

Grupos exibem nomes e totais individuais apenas aos membros. Alertas podem
usar abertura geral, abertura de lote ou data personalizada. O worker processa
os avisos sem depender da página aberta. Recomendações locais utilizam
preferências consentidas e compras pagas.

## Permissões

- Público: eventos, disponibilidade, mapas, comparador, regras, cadastro/login.
- Cliente: próprios dados, documentos, reservas, pagamentos, ingressos,
  grupos dos quais participa, alertas e recomendações.
- Administrador: gestão de usuários/eventos/lotes/mapas, análise documental,
  relatórios e portaria.
- Campos `papel` enviados no cadastro ou perfil não concedem administração.

## Escopo de demonstração

Por escolha do usuário, gateway externo e IA não são exigidos para executar:
o pagamento usa simulador identificado, e a recomendação padrão é local.
Há adaptador Gemini opcional com retorno local se falhar; chamadas reais
dependem de credenciais e não foram homologadas nesta entrega.
Não se declara adequação legal ou certificação PCI-DSS.

O modelo de arquitetura do PDF pede `db.Model` e classes por operação. Essas
orientações não foram copiadas: manteve-se a adaptação anterior para MySQL,
SQL puro, funções simples e sessão, com as pastas de camadas existentes.
