# Production Readiness

Status: ADRs 009 a 013 APROVADOS para USO PROPRIO. O sistema nao esta autorizado para dados reais.

Os ADRs de PostgreSQL, criptografia, autenticacao de producao, backup/restauracao e retencao LGPD foram aprovados pelo dono em 2026-07-12. Essa aprovacao nao autoriza publicacao, uso de dados reais, integracoes reais, SaaS ou merge automatico do PR no 10.

## Checklist

| Area | Condicao | Status |
| --- | --- | --- |
| Banco | PostgreSQL gerenciado via `DATABASE_URL` | PENDENTE |
| Migrations | Aplicadas formalmente e revisadas | PENDENTE |
| Criptografia | `BBB_DATA_ENCRYPTION_KEY` forte em cofre | PENDENTE |
| Autenticacao | `BBB_AUTH_SECRET` forte, cookie Secure e demo-login bloqueado | PARCIAL |
| Backup | Backup externo diario configurado | PENDENTE |
| Restauracao | Restore externo testado | PENDENTE |
| LGPD | Politica de retencao e atendimento aprovada | PENDENTE |
| Consentimento | Finalidade, status e opt-out validados | PARCIAL |
| Logs | Logs mascarados auditados | PARCIAL |
| Testes | Backend, build, E2E e seguranca aprovados | PARCIAL |
| Credenciais | Nenhum segredo no Git; secrets em provedor seguro | PENDENTE |
| Publicacao | Nova publicacao aprovada pelo dono | PENDENTE |
| Rollback | Plano validado com tag/backup | PENDENTE |

## Gate Tecnico

`APP_MODE=production` deve falhar se qualquer uma destas configuracoes faltar:

- `DATABASE_URL`
- `BBB_DATA_ENCRYPTION_KEY`
- `BBB_AUTH_SECRET`
- `MIGRATIONS_APPLIED`
- `BACKUP_CONFIGURED`
- `CONSENT_REQUIRED`
- `LOGS_MASKED`
- `HTTPS_EXPECTED`
- `CRITICAL_TESTS_APPROVED`

## Classificacao Atual

AINDA SOMENTE DEMO.

## Proxima Aprovacao Necessaria

Antes de dados reais: provisionar secrets reais em cofre/provedor, aplicar migrations em PostgreSQL gerenciado, validar backup/restore externo, rodar auditoria final e obter aprovacao explicita do dono para uso real e publicacao.
