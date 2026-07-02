# Modelo de Dados - BBB Consig CRM

## Banco atual
SQLite local em `backend/app.db`, com migrations em `backend/migrations`, permanece restrito a desenvolvimento, testes locais e MVP controlado.

## Producao real
Producao real com dados de clientes exige PostgreSQL gerenciado via `DATABASE_URL` configurada somente no painel seguro do provedor. Nunca commitar URL real de banco e nunca colar `DATABASE_URL` real no chat.

As migrations SQL em `backend/migrations` sao legado seguro para SQLite local. Em PostgreSQL, o schema inicial deve ser criado pelos modelos SQLAlchemy e as migrations legadas sao registradas em `schema_migrations` sem executar SQL especifico de SQLite.

Uso com dados reais continua bloqueado ate concluir criptografia em repouso, autenticacao segura, backup/restore, monitoramento e revisao LGPD.

## Tabelas existentes
- `leads`
- `clientes`
- `propostas`
- `tarefas`
- `whatsapp_messages`

## Tabelas de seguranca/LGPD
- `users`
- `audit_logs`
- `consents`
- `simulations`

Todas as tabelas possuem `id`, `created_at` e `updated_at`. Campos legados como `data_criacao` e `criado_em` permanecem para compatibilidade do MVP.

## Campos sensiveis
- CPF
- Telefone
- Email
- Beneficio
- Banco de pagamento
- Observacoes quando contiverem dados pessoais

## Campos que precisam de protecao
- `leads.cpf`, `leads.telefone`, `leads.email`
- `clientes.cpf`, `clientes.telefone`, `clientes.email`, `clientes.beneficio`, `clientes.banco_pagamento`
- payloads de simulacao e metadados de auditoria

## Audit log obrigatorio
- Login
- Criacao/edicao/soft delete de cliente
- Registro de opt-in
- WhatsApp simulado
- Simulacao INSS/FGTS

## Soft delete
Tabelas com dados pessoais devem usar `deleted_at` antes de remocao definitiva.

## ERD
```mermaid
erDiagram
  leads ||--o{ tarefas : gera
  clientes ||--o{ propostas : possui
  clientes ||--o{ consents : autoriza
  clientes ||--o{ simulations : recebe
  users ||--o{ audit_logs : registra
  leads {
    int id
    string nome
    string cpf
    string telefone
    string email
    string origem
    string produto_interesse
    string status
    string prioridade
    string responsavel
    string proximo_contato
  }
  clientes {
    int id
    string nome
    string cpf
    string telefone
    string email
    string beneficio
    string convenio
    datetime deleted_at
  }
  consents {
    int id
    int customer_id
    string channel
    bool granted
    datetime created_at
    datetime revoked_at
  }
  audit_logs {
    int id
    string actor
    string action
    string entity_type
    int entity_id
    string metadata_json
    datetime created_at
  }
```
