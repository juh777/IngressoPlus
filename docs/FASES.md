# Fases do Projeto — Sistema de Ingressos

Checklist para acompanhar o desenvolvimento por partes. Marque cada item
conforme for concluído e validado (rodando via Docker).

## Fase 0 — Estrutura Base
- [x] Estrutura de pastas (backend, frontend, docs)
- [x] Backend Flask: application factory, config, extensões
- [x] Docker Compose (PostgreSQL + backend + frontend)

## Fase 1 — CRUD Base (concluída)
- [x] Model `Usuario` (nome, email, cpf, telefone, senha_hash)
- [x] Model `Evento` (nome, local, datas, categoria)
- [x] Service `usuario_service` (validação de email/cpf, hash de senha, unicidade)
- [x] Service `evento_service` (validação de datas)
- [x] Controller `/api/usuarios` (GET, POST, PUT, DELETE)
- [x] Controller `/api/eventos` (GET, POST, PUT, DELETE)
- [x] Frontend: listagem + formulário de Eventos
- [x] Frontend: listagem + formulário de Usuarios
- [x] Testado rodando via `docker compose up`
- [x] Migrations geradas (`flask db init/migrate/upgrade`)

## Fase 2 — Autenticação
- [ ] Login/registro (JWT ou sessão)
- [ ] Middleware de autenticação nas rotas protegidas
- [ ] Tela de login/cadastro no frontend
- [ ] Associar usuário logado às ações (compras, grupos, etc.)

## Fase 3 — Lotes e Ingressos
- [ ] Model `Lote` (evento, nome, preço, quantidade, taxa de conveniência)
- [ ] Model `Ingresso` (lote, comprador, status)
- [ ] CRUD de lotes vinculado a um evento
- [ ] Cálculo/exibição de taxas por lote

## Fase 4 — Compras
- [ ] Fluxo de compra (seleção de lote → checkout)
- [ ] Model `Pedido` / `ItemPedido`
- [ ] Histórico de compras do usuário

## Fase 5 — Notificações
- [ ] Lembretes configuráveis antes da abertura das vendas (e-mail/push)
- [ ] Monitoramento em tempo real de disponibilidade/lotes
- [ ] Notificação instantânea de mudança de lote ou esgotamento

## Fase 6 — Perfil e Autopreenchimento
- [ ] Perfil de usuário com dados salvos com segurança
- [ ] Autopreenchimento de formulários de compra

## Fase 7 — Compra Expressa
- [ ] Preparação automática de pedido antes da abertura
- [ ] Finalização automática assim que as vendas abrirem

## Fase 8 — Confiança e Comparação
- [ ] Módulo de verificação de autenticidade de ingressos
- [ ] Comparação de taxas entre canais de venda

## Fase 9 — Mapa Interativo
- [ ] Mapa do evento com setores/assentos disponíveis
- [ ] Seleção de assento no fluxo de compra

## Fase 10 — Grupos de Compra
- [ ] Model `GrupoCompra` e participantes
- [ ] Divisão de valores e controle de pagamentos do grupo

---

**Convenção:** cada fase segue sempre a mesma ordem de trabalho —
Model → Service → Controller → Frontend → teste via Docker — igual ao que foi
feito na Fase 1.
