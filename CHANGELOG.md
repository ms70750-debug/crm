# Changelog

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
