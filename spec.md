# BBB Consig CRM - Especificacao Inicial

## Escopo da primeira versao
CRM operacional para credito consignado com dashboard, leads, clientes, consultas simuladas INSS/FGTS, propostas, tarefas, WhatsApp simulado, treinamentos e administracao.

## Pipeline do lead
Novo lead -> Qualificado -> Aguardando documentos -> Simulado -> Proposta enviada -> Digitado -> Pendente banco -> Aprovado -> Pago -> Perdido

## Caminhos criticos
- Criar, listar, editar, filtrar e alterar status de leads.
- Criar, listar e editar clientes.
- Criar, listar e alterar status de propostas vinculadas a clientes.
- Criar, listar e concluir tarefas.
- Gerar e registrar mensagens no WhatsApp simulado sem envio real.
- Carregar resumo do dashboard com dados do banco SQLite.

## Regras de simulacao
- Consultas INSS e FGTS exibem resultados ficticios.
- Evolution API deve aparecer como configuracao simulada, sem chamada externa.
- Dados iniciais sao seed ficticio.
