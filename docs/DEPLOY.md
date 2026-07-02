# Deploy

## Status
Preparado para deploy controlado/teste. Producao real com dados de clientes continua bloqueada.

## Deploy controlado MVP - 2026-07-02

Status atual: preparado para acao manual no provedor. Ainda nao ha URL publica documentada para backend ou frontend.

| Item | Provedor | Status | URL |
|---|---|---|---|
| Backend | Render | Pendente criacao/validacao no painel | Pendente |
| Frontend | Vercel | Pendente criacao/validacao no painel | Pendente |

Este deploy e somente para homologacao com dados ficticios ou anonimizados.

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
- `BBB_AUTH_SECRET`
- `CORS_ORIGINS`
- `DATABASE_URL`
- `EVOLUTION_API_MODE`

### Frontend Vercel
- `VITE_API_URL`

### Opcionais nesta fase
- `BACKEND_HOST`
- `BACKEND_PORT`
- `EVOLUTION_API_URL`
- `EVOLUTION_API_TOKEN`

`EVOLUTION_API_URL` e `EVOLUTION_API_TOKEN` devem ficar vazios enquanto WhatsApp estiver em modo simulacao.

## CORS

O `render.yaml` mantem `CORS_ORIGINS=http://localhost:5173` como valor temporario para o primeiro deploy do backend.

Depois que a Vercel gerar a URL real do frontend, alterar `CORS_ORIGINS` no Render para a URL da Vercel. Manter localhost apenas se tambem for necessario testar desenvolvimento local.

## Smoke test controlado

### Backend
1. Abrir `https://URL-DO-RENDER/healthz`.
2. Confirmar resposta 200 com `status: ok`.
3. Revisar logs do Render e confirmar que nenhum segredo foi impresso.

### Frontend
1. Abrir `https://URL-DA-VERCEL/login`.
2. Entrar com usuario demo.
3. Validar dashboard, leads, clientes, propostas, tarefas e WhatsApp simulado.
4. Confirmar que nenhuma informacao real foi necessaria.

## Sequencia manual recomendada
1. Criar backend no Render pelo Blueprint `render.yaml`.
2. Configurar variaveis do backend no painel seguro.
3. Testar `/healthz` publico.
4. Criar frontend na Vercel com root directory `frontend`.
5. Configurar `VITE_API_URL` com a URL publica do Render.
6. Fazer deploy do frontend.
7. Atualizar `CORS_ORIGINS` no Render com a URL real da Vercel.
8. Redeploy do backend.
9. Rodar smoke test com usuarios e dados ficticios.
