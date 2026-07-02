# BBB Consig CRM - Especificacao Inicial

## Escopo da primeira versao
CRM operacional para credito consignado com dashboard, leads, clientes, consultas simuladas INSS/FGTS, propostas, tarefas, WhatsApp simulado, treinamentos e administracao.

## Classificacao e limites atuais
- Classificacao: USO_PROPRIO.
- Fase atual: MVP controlado.
- Publico esperado: dono da operacao e equipe interna restrita.
- Capacidade alvo: ate 10 usuarios internos no MVP.
- Dados permitidos: ficticios ou anonimizados.
- Dados proibidos: CPF real, conta bancaria real, beneficio real, margem real e contrato real.
- Producao real futura: condicionada a PostgreSQL, backup/restore, monitoramento, criptografia em repouso, autenticacao segura e revisao LGPD.

Aviso obrigatorio: Este projeto ainda nao esta liberado para operacao real com dados pessoais de clientes. Uso atual permitido apenas para teste controlado com dados ficticios.

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
