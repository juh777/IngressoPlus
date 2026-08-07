# Roadmap — Próximas Etapas

Requisitos levantados a partir de observações de usuários, a serem
implementados em partes após a conclusão do CRUD base (Parte 1: Eventos e
Usuários).

1. **Lembretes de abertura de vendas** — notificações push/e-mail
   configuráveis antes da abertura das vendas de um evento.
2. **Perfil com autopreenchimento** — salvamento seguro de dados pessoais
   (nome, CPF, documento) para reaproveitar em novas compras.
3. **Compra Expressa** — preenchimento e finalização automática do pedido no
   instante em que as vendas abrem.
4. **Monitoramento em tempo real** — acompanhar disponibilidade/lotes de
   ingressos e notificar instantaneamente sobre mudanças ou esgotamento.
5. **Verificação de autenticidade** — módulo para validar ingressos ou
   restringir a compra a canais oficiais parceiros.
6. **Comparação de taxas** — exibir taxas de conveniência de diferentes
   canais de venda lado a lado.
7. **Mapa interativo do evento** — visualização de setores e assentos
   disponíveis.
8. **Grupos de compra** — gestão de compras em grupo, com divisão de valores
   e controle de quem já pagou.

Cada item será tratado como um módulo próprio (novos models, services,
controllers e telas), construído em cima da base de Eventos e Usuários já
implementada.
