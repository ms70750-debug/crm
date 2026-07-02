# Changelog

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
