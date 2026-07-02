# Deploy

## Status
Deploy controlado/teste online validado. Producao real com dados de clientes continua bloqueada.

## Deploy controlado MVP - 2026-07-02

Status atual: online e validado para homologacao com dados ficticios.

| Item | Provedor | Status | URL |
|---|---|---|---|
| Backend | Render | Publicado e health check validado | `https://crm-2340.onrender.com` |
| Frontend | Vercel | Publicado e login demo validado | `https://crm-sepia-beta.vercel.app` |

Este deploy e somente para homologacao com dados ficticios ou anonimizados.

Health check publico: `https://crm-2340.onrender.com/healthz`

Resposta esperada:
```json
{"status":"ok","service":"BBB Consig CRM API"}
```

Login demo: validado com sucesso no ambiente Vercel.

## Bloqueios atuais
- Autenticacao atual e adequada apenas para MVP controlado.
- Falta hardening completo de producao real.
- SQLite local nao e banco de producao.
- Integracoes externas estao bloqueadas por design.
- Dados reais de clientes nao estao liberados.

## Pre-requisitos antes de publicar
- Revisao de seguranca.
- Banco PostgreSQL.
- Criptografia/protecao de dados pessoais em repouso.
- Autenticacao com sessao segura para producao.
- Segredos em cofre/env seguro.
- HTTPS.
- Backups.
- Monitoramento.
- Testes E2E e API passando.
- Auditoria LGPD.

## Checklist pre-deploy
- `npm run build`
- testes backend
- testes E2E
- `npm audit`
- confirmar `APP_ENV=production` no provedor
- confirmar `.env` fora do Git
- revisar logs sem CPF/email/telefone
- validar opt-in antes de comunicacao
- validar snapshot de simulacao

## Variaveis obrigatorias no deploy controlado

Somente configure valores no painel seguro do provedor. Nao cole segredos no chat e nao versione `.env`.

### Backend Render
- `APP_ENV`
- `PYTHON_VERSION`
- `BBB_AUTH_SECRET`
- `CORS_ORIGINS`
- `DATABASE_URL`
- `REAL_DATA_MODE`
- `EVOLUTION_API_MODE`

### Frontend Vercel
- `VITE_API_URL`

### Opcionais nesta fase
- `BACKEND_HOST`
- `BACKEND_PORT`
- `EVOLUTION_API_URL`
- `EVOLUTION_API_TOKEN`

`EVOLUTION_API_URL` e `EVOLUTION_API_TOKEN` devem ficar vazios enquanto WhatsApp estiver em modo simulacao.

## PostgreSQL para producao real

Producao real com dados de clientes exige PostgreSQL gerenciado. SQLite permanece apenas para desenvolvimento, testes locais e MVP controlado.

Para preparar PostgreSQL:
1. Criar um banco PostgreSQL gerenciado no provedor seguro escolhido.
2. Configurar a `DATABASE_URL` real somente no painel seguro do Render.
3. Nunca colar `DATABASE_URL` real no chat.
4. Nunca commitar `.env`.
5. Manter `REAL_DATA_MODE=false` ate concluir criptografia em repouso, autenticacao segura, backup/restore, monitoramento e revisao LGPD.
6. Apos configurar `DATABASE_URL`, redeployar o backend.

Smoke test apos configurar PostgreSQL:
- `GET /healthz`
- Login demo.
- Criacao de cliente ficticio.
- Registro de opt-in ficticio.
- Simulacao ficticia.

Rollback:
- Se o deploy com PostgreSQL falhar, pausar o uso online ou restaurar a `DATABASE_URL` anterior de teste controlado.
- Nao migrar dados reais sem backup e restore testados.
- Nao inserir dados reais antes de concluir todos os controles de seguranca e LGPD.

## Migrations PostgreSQL

As migrations de banco ficam separadas por estrategia:
- Migrations legadas na raiz de `backend/migrations/` e migrations em `backend/migrations/sqlite/` sao usadas pelo SQLite local/MVP controlado.
- Migrations em `backend/migrations/postgres/` sao reservadas para PostgreSQL gerenciado.

Migrations PostgreSQL devem usar tipos compativeis com PostgreSQL, como `TIMESTAMPTZ` para data/hora com fuso quando aplicavel. Nao usar `DATETIME` em migration PostgreSQL.

`Base.metadata.create_all` nao e estrategia final de producao real. Ele permanece apenas como bootstrap local/controlado. Em `APP_ENV=production` com PostgreSQL, schema e migrations devem ser aplicados de forma formal, apos banco gerenciado criado, backup/restore definido e aprovacao explicita.

Nao executar migration em banco real nesta fase. O projeto continua limitado a dados ficticios ou anonimizados.

## CORS

O Render esta configurado para aceitar:
`http://localhost:5173,https://crm-sepia-beta.vercel.app`

Manter localhost apenas para desenvolvimento local. A URL real da Vercel deve permanecer no CORS enquanto o frontend publico estiver ativo.

## Versao do Python no Render

O backend deve rodar com Python `3.12.8` no Render. A versao esta fixada no `render.yaml` por `PYTHON_VERSION=3.12.8` e tambem registrada em `.python-version`.

Nao permitir que o Render escolha automaticamente Python `3.14.x` neste MVP controlado. Essa versao pode nao ter wheels compativeis para dependencias atuais, especialmente `pydantic-core`, fazendo o build tentar compilar com Rust/maturin e falhar no ambiente do provedor.

Se o deploy falhar durante `pip install -r requirements.txt` com erro em `pydantic-core`, confira primeiro a versao de Python usada nos logs do Render.

## Smoke test controlado

### Backend
1. Abrir `https://crm-2340.onrender.com/healthz`.
2. Confirmar resposta 200 com `status: ok`.
3. Revisar logs do Render e confirmar que nenhum segredo foi impresso.

### Frontend
1. Abrir `https://crm-sepia-beta.vercel.app/login`.
2. Entrar com usuario demo.
3. Validar dashboard, leads, clientes, propostas, tarefas e WhatsApp simulado.
4. Confirmar que nenhuma informacao real foi necessaria.

## Proximos passos antes de producao real

Antes de qualquer uso com dados reais, implementar e validar:
- PostgreSQL gerenciado.
- Criptografia/protecao de dados pessoais em repouso.
- Autenticacao segura para producao.
- Backup e restore testados.
- Monitoramento e alertas.
- Revisao LGPD final.
