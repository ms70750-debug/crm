# Changelog

## 2026-07-15 - Backup oficial com Supabase CLI

### Alterado
- Substituido o fluxo ativo de backup criptografado por Supabase CLI oficial, separando roles, schema e dados.
- Adicionado pacote unico criptografado `crm-supabase-backup.tar.enc` com manifesto/checksums seguros.
- Criada ADR 009 documentando a decisao e o rollback por tag.

### Mantido
- Nenhum backup real foi executado, nenhuma restauracao foi executada, nenhum secret foi revelado e nenhuma publicacao foi realizada.

## 2026-07-15 - Escopo seguro do pg_dump de producao

### Corrigido
- Limitado o `pg_dump` criptografado ao schema `public`, comprovado como schema do CRM pelas migrations e modelos.
- Adicionado diagnostico sanitizado para SQLSTATE, tipo de objeto, schema e classe de erro sem imprimir stderr bruto.
- Documentado no manifesto os schemas gerenciados pelo Supabase excluidos do dump e as extensoes encontradas.

### Mantido
- Nenhum novo backup real foi executado, nenhuma restauracao foi executada, nenhum secret foi revelado e nenhuma publicacao foi realizada.

## 2026-07-15 - Saida vazia do pg_dump no backup

### Corrigido
- Validado o destino do dump antes do `pg_dump`, incluindo diretorio, escrita, espaco livre e caminho absoluto.
- Separada falha real do `pg_dump` de arquivo vazio, evitando mascarar erro de banco como `PGDUMP_OUTPUT_FILE_ERROR`.
- Bloqueada a continuidade para criptografia e upload quando o `pg_dump` termina sem gerar dump nao vazio.

### Mantido
- Nenhuma nova tentativa de backup foi executada, nenhuma restauracao foi executada, nenhum secret foi revelado e nenhuma publicacao foi realizada.

## 2026-07-15 - pg_dump 17 no workflow de backup

### Corrigido
- Ajustado o workflow `Supabase Encrypted Backup` para priorizar `/usr/lib/postgresql/17/bin` no `PATH` apos instalar `postgresql-client-17`, evitando que o runner use um `pg_dump` antigo no preflight.

### Mantido
- Nenhuma nova tentativa de backup foi executada, nenhuma restauracao foi executada, nenhum secret foi revelado e nenhuma publicacao foi realizada.

## 2026-07-15 - Diagnostico seguro complementar de pg_dump

### Adicionado
- Criados codigos internos `BACKUP_DIAGNOSTIC_CODE` para falhas de `pg_dump`, DNS, SSL, autenticacao, permissao, timeout, saida vazia e criptografia.
- Incluidas flags seguras sobre binario encontrado, arquivo de saida criado, arquivo nao vazio, criptografia iniciada e upload iniciado.
- Ampliados testes mockados para garantir que host, usuario, senha, URL e stderr bruto nao sejam exibidos nos diagnosticos.

### Mantido
- Nenhum backup real foi executado, nenhuma restauracao foi executada, nenhum secret foi revelado e nenhuma publicacao foi realizada.

## 2026-07-12 - Driver psycopg no preflight de backup

### Corrigido
- Normalizadas URLs PostgreSQL para `postgresql+psycopg://` em conexoes SQLAlchemy do preflight, evitando dependencia implicita de `psycopg2`.
- Mantido `pg_dump` recebendo a conexao por ambiente seguro, sem URL em argumentos e sem exposicao de host, usuario, senha ou chave.

### Mantido
- Nenhum backup real foi criado, nenhum Supabase real foi acessado, nenhum secret foi exposto e nenhuma publicacao foi realizada.

## 2026-07-12 - Diagnostico seguro de pg_dump

### Corrigido
- Ajustado backup criptografado para passar a conexao ao `pg_dump` por ambiente seguro em vez de argumento visivel.
- Adicionadas categorias seguras para falhas de `pg_dump`, sem stderr bruto e sem expor URL, host, usuario ou senha.
- Alinhado workflow `Supabase Encrypted Backup` para instalar cliente PostgreSQL compativel e registrar somente versoes principais e compatibilidade.

### Mantido
- Nenhum backup real foi criado, nenhum workflow real de backup/restore foi executado e o Supabase real nao foi alterado.

## 2026-07-12 - Backup externo criptografado

### Aprovado
- ADR 014 aprovada pelo dono do projeto para USO PROPRIO em 2026-07-12.
- Mantidas como pendentes a chave real, armazenamento externo, primeiro backup real, primeiro restore real controlado e agendamento.

### Adicionado
- Proposta a ADR 014 para backup externo criptografado com `pg_dump`, criptografia autenticada, checksum SHA-256 e restore testavel.
- Criados scripts `create_encrypted_postgres_backup.py` e `verify_encrypted_backup_restore.py` para backup criptografado e validacao de restore em PostgreSQL temporario.
- Criados workflows manuais `Supabase Encrypted Backup` e `PostgreSQL Backup Restore Test`, sem agendamento e sem upload externo real.
- Adicionados testes de criptografia, checksum, manifesto seguro, chave ausente/incorreta, artifact seguro, restore ficticio e workflows.

### Mantido
- Nenhum backup real foi criado, nenhum dado real foi usado, nenhuma credencial real foi configurada e nenhuma publicacao foi realizada.

## 2026-07-12 - Permissoes backend-only Supabase

### Adicionado
- Documentada a decisao `BACKEND-ONLY` para o Supabase: frontend sem CRUD direto, backend como unico caminho autorizado e `service_role` proibido no frontend.
- Criada migration PostgreSQL `2026_07_12_backend_only_permissions.sql` para revogar grants diretos de `PUBLIC`, `anon` e `authenticated` nas 12 tabelas do CRM.
- Criado rollback manual documentado para restaurar somente grants explicitamente controlados, mediante aprovacao futura.
- Criado workflow `PostgreSQL Backend Only Validation` com PostgreSQL 16 descartavel para validar cadeia de 5 migrations, bloqueio de grants, usuario `backend_app`, rollback e preservacao de dados ficticios.

### Mantido
- Nenhuma permissao real foi alterada nesta tarefa.
- Nenhuma migration foi aplicada no Supabase real, nenhum dado real foi usado e nenhuma publicacao foi realizada.

## 2026-07-12 - Auditoria de permissoes Supabase

### Adicionado
- Criado workflow manual `Supabase Permissions Audit` para auditar grants, owners, RLS, policies e roles sem alterar o banco.
- Criado script `backend/scripts/audit_supabase_permissions.py` para classificar tabelas como SEGURO, ATENCAO ou CRITICO e recomendar BACKEND-ONLY ou RLS OBRIGATORIO.
- Adicionados testes de classificacao para grants de `public`, `anon`, `authenticated`, tabelas sem RLS, mascaramento e estrategia backend-only.

### Mantido
- Nenhum GRANT, REVOKE, RLS, policy, migration, dado, credencial, deploy ou publicacao foi executado nesta tarefa.

## 2026-07-12 - Auditoria readonly Supabase

### Adicionado
- Criado workflow manual `Supabase Readonly Audit` para auditar o Supabase real sem aplicar migrations, DDL ou DML.
- Criado script `backend/scripts/audit_supabase_readonly.py` com transacao `READ ONLY`, bloqueio de comandos de escrita, relatorio seguro, job summary e artifact `supabase-readonly-audit`.
- Adicionados testes para validar bloqueio de escrita, mascaramento de erros, ausencia de segredos e relatorio apenas com metadados/contagens.

### Mantido
- Nenhum Supabase real acessado nesta tarefa, nenhuma migration aplicada, nenhum dado inserido, nenhum segredo exposto e nenhuma publicacao realizada.

## 2026-07-12 - Workflow unitario de apply Supabase

### Adicionado
- Criado workflow manual `Supabase Migration Single Apply` para aplicar somente uma migration PostgreSQL por execucao.
- Criado script `backend/scripts/apply_single_postgres_migration.py` com confirmacao explicita, controle de ordem, checksum, bloqueio de reaplicacao e teste transacional antes do apply.
- Adicionados testes para migration invalida, confirmacao invalida, ordem incorreta, reaplicacao, checksum divergente e erro com rollback transacional.

### Mantido
- Nenhuma migration real aplicada, nenhum Supabase real acessado, nenhum segredo exposto e nenhuma publicacao realizada.

## 2026-07-12 - Bootstrap PostgreSQL para Supabase vazio

### Adicionado
- Criada migration `backend/migrations/postgres/2026_07_01_000_postgres_bootstrap_schema.sql` para schema PostgreSQL inicial vazio.
- Documentado o schema base PostgreSQL em `docs/DATA-MODEL.md`.
- Reforcado o dry-run para validar cadeia em schema vazio antes de listar migrations.

### Mantido
- Nenhum Supabase real acessado, nenhuma migration real aplicada, nenhum dado real usado e nenhuma publicacao realizada.

## 2026-07-12 - Plano de conexao Supabase

### Adicionado
- Criado `docs/SUPABASE-CONNECTION-PLAN.md` com inventario de variaveis, migrations, GitHub Actions, backup, rollback e criterios para futura conexao controlada ao projeto Supabase.

### Mantido
- Nenhuma migration aplicada, nenhuma credencial real configurada, nenhuma publicacao realizada e dados reais continuam proibidos.

## 2026-07-12 - Correcao dos bloqueadores pre-merge do PR 10

### Corrigido
- Adicionada revogacao server-side de sessao no logout, com armazenamento de hash do identificador da sessao.
- Alinhados `docs/LGPD.md` e `docs/BACKUP-RESTORE.md` aos ADRs 009 a 013 aprovados para USO PROPRIO.
- Bloqueado deploy automatico da branch `feature/real-data-readiness-2026-07-12` no `frontend/vercel.json`.

### Mantido
- Dados reais, credenciais reais, WhatsApp real, PostgreSQL real e publicacao de producao continuam proibidos sem nova aprovacao explicita.

## 2026-07-12 - Aprovacao arquitetural para uso proprio

### Alterado
- ADRs 009 a 013 marcados como APROVADO pelo dono do projeto para escopo de USO PROPRIO.
- Registrado que a aprovacao dos ADRs nao autoriza dados reais, publicacao, integracoes reais, SaaS ou merge automatico do PR no 10.
- Mantida exigencia de auditoria final, credenciais seguras e aprovacao explicita antes de qualquer ativacao real.

## 2026-07-12 - Preparacao segura para dados reais

### Adicionado
- Propostos ADRs 009 a 013 para PostgreSQL, criptografia, autenticacao, backup/restauracao e retencao LGPD.
- Criada fundacao de readiness para bloquear `APP_MODE=production` sem controles obrigatorios.
- Adicionada camada isolada de protecao de dados com envelope versionado, autenticacao e hash separado de CPF.
- Criadas migrations aditivas para soft delete, campos protegidos, consentimento ampliado e auditoria de backup.
- Adicionados testes de criptografia, readiness, soft delete/restauracao, consentimento, migration temporaria e backup/restore ficticio.

### Bloqueios preservados
- `APP_MODE=demo` continua sendo o padrao seguro.
- Dados reais continuam proibidos ate auditoria final e aprovacao explicita.
- Nenhuma credencial real, conexao PostgreSQL real, publicacao ou merge foi realizado nesta preparacao.

## 2026-07-12 - Correcao documental do PR 9

### Corrigido
- Atualizado o relatorio de recuperacao para registrar o PR no 9 aberto.
- Atualizado o hash final revisado para `0f037840a576c5ac4f7e0350d3d89469ef6661e5`.
- Mantida a classificacao como MVP controlado para uso interno com dados ficticios.

## 2026-07-12 - Recuperacao segura pos-auditoria funcional

### Corrigido
- Adicionado `APP_MODE=demo` para manter o CRM em demonstracao controlada.
- Bloqueado CPF matematicamente valido em cadastros e simulacoes enquanto o modo demo estiver ativo.
- Reforcada sessao com cookie HttpOnly, SameSite adequado e Secure em producao.
- Criado logout auditado e login demo por perfil sem expor senha na tela.
- Mantida Evolution API em modo 100% simulado com status visivel.
- Adicionadas acoes seguras de status/exclusao em leads, propostas e tarefas conforme permissao.
- Adicionado opt-out de WhatsApp para consentimento.

### Testes
- Backend passou de 32 para 36 testes aprovados.
- E2E atualizado para validar login demo, aviso de ambiente, opt-in/opt-out, WhatsApp simulado, INSS simulado e Admin.
- Build frontend segue aprovado, com alerta conhecido de bundle acima de 500 kB.

### Bloqueios preservados
- Nao houve migracao para PostgreSQL.
- Nao houve publicacao em Render/Vercel.
- Nao houve liberacao para dados reais ou SaaS.
- Criptografia em repouso e multi-tenancy seguem bloqueados por ADR e decisao comercial.

## 2026-07-03 - Workflow controlado para aplicar migrations Supabase

### Adicionado
- Criado workflow manual separado para aplicacao das migrations PostgreSQL.
- Exigida confirmacao `APLICAR_MIGRATIONS_SUPABASE`.
- Mantido `REAL_DATA_MODE=false`.
- Mantida proibicao de dados reais.

## 2026-07-02 - Mascara reforcada da DIRECT_URL

### Corrigido
- Reforcada a mascara da DIRECT_URL para ocultar usuario e host completos.
- Mantida protecao contra vazamento de senha e URL completa.
- Mantido dry-run sem aplicacao de migrations.

## 2026-07-02 - Tratamento seguro de DIRECT_URL invalida

### Corrigido
- Corrigida falha segura quando `DIRECT_URL` contem placeholder ou formato invalido.
- Evitado traceback bruto com `urlsplit`.
- Mantida protecao contra vazamento de segredo.

## 2026-07-02 - Workflow dry-run Supabase

### Alterado
- Criado workflow manual de dry-run das migrations Supabase via GitHub Actions.
- Usado secret `SUPABASE_DIRECT_URL` sem expor senha.
- Mantida proibicao de dados reais.
- Nenhuma migration e aplicada por esse workflow.

## 2026-07-02 - Preparacao Supabase PostgreSQL

### Alterado
- Documentada configuracao Supabase PostgreSQL.
- Diferenciado `DATABASE_URL` para runtime e `DIRECT_URL` para migrations/admin.
- Preparado script seguro para dry-run/aplicacao manual de migrations PostgreSQL.
- Mantido bloqueio de dados reais e `REAL_DATA_MODE=false`.

## 2026-07-02 - Correcao da estrategia de migrations PostgreSQL antes do merge

### Corrigido
- Separadas migrations SQLite e PostgreSQL para preparacao de producao real futura.
- Criada migration PostgreSQL com `TIMESTAMPTZ` e sem `DATETIME`.
- Documentado que `Base.metadata.create_all` nao e estrategia final de producao real.
- Mantido bloqueio de dados reais e `REAL_DATA_MODE=false`.

## 2026-07-02 - Preparacao PostgreSQL para producao real

### Alterado
- Suporte/documentacao para PostgreSQL em producao real.
- SQLite mantido apenas para desenvolvimento, testes locais e MVP controlado.
- Runtime checks reforcados para `DATABASE_URL` e `REAL_DATA_MODE`.
- ADR de PostgreSQL atualizada para Accepted.
- Uso com dados reais continua bloqueado ate criptografia, autenticacao segura, backup/restore, monitoramento e revisao LGPD.

## 2026-07-02 - Deploy controlado online validado

### Alterado
- Backend Render publicado.
- Frontend Vercel publicado.
- Health check validado.
- Login demo validado.
- CORS ajustado para URL real da Vercel.
- Uso com dados reais continua proibido.

## 2026-07-02 - Fix deploy Render Python

### Corrigido
- Fixada versao estavel do Python para backend no Render.
- Documentado erro de Python 3.14/pydantic-core no deploy.
- Preservado deploy controlado apenas com dados ficticios.

## 2026-07-02 - Deploy controlado MVP

### Alterado
- Documentada preparacao/validacao de deploy controlado para Render e Vercel.
- Registrado status pendente de URLs publicas ate criacao manual nos provedores.
- Documentado CORS temporario com localhost e ajuste necessario apos URL real da Vercel.
- Smoke test controlado descrito para backend, frontend e fluxo ficticio.
- Restricoes contra dados reais preservadas.

## 2026-07-02 - Hardening pre-producao Yntelli

### Alterado
- Classificacao explicita do projeto como USO_PROPRIO - MVP CONTROLADO.
- Bloqueio documental para dados reais: uso permitido apenas com dados ficticios ou anonimizados.
- Capacidade documentada para ate 10 usuarios internos no MVP.
- Regras de negocio atualizadas para visualizacao operacional por perfil, parceiro limitado, opt-in, logs mascarados e snapshots de simulacao.
- `README.md` e `spec.md` atualizados com fase atual, limites de uso e caminho futuro para producao real.

### Adicionado
- ADRs de classificacao, PostgreSQL para producao real, criptografia em repouso, autenticacao segura e backup/restore/monitoramento.
- `docs/MAINTENANCE.md` com check-up semanal, mensal e auditoria trimestral.
- Validacao de ambiente em runtime quando `APP_ENV=production`, sem expor valores sensiveis em logs.

## 2026-07-01

### Adicionado
- Fundacao inicial do BBB Consig CRM com backend FastAPI, frontend React e SQLite local.
- Esteira de leads com detalhe, timeline, historico, filtros, prioridade, conversao para cliente e geracao de proposta simulada.

### Correcao Yntelli
- Iniciada frente de fundacao, seguranca LGPD e testes minimos.
- Projeto permanece em ambiente local/demo, sem publicacao em producao.
