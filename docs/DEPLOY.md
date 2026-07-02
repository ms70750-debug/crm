# Deploy

## Status
Preparado para deploy controlado/teste. Producao real com dados de clientes continua bloqueada.

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
