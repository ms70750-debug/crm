# Deploy

## Status
NAO PUBLICADO.

## Bloqueios atuais
- Autenticacao ainda e minima/demo.
- Falta hardening de producao.
- SQLite local nao e banco de producao.
- Integracoes externas estao bloqueadas por design.

## Pre-requisitos antes de publicar
- Revisao de seguranca.
- Banco PostgreSQL.
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
- confirmar `.env` fora do Git
- revisar logs sem CPF/email/telefone
- validar opt-in antes de comunicacao
- validar snapshot de simulacao
