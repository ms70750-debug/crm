# Production Readiness

Status: ADRs 009 a 013 APROVADOS para USO PROPRIO. O sistema nao esta autorizado para dados reais.

Os ADRs de PostgreSQL, criptografia, autenticacao de producao, backup/restauracao e retencao LGPD foram aprovados pelo dono em 2026-07-12. Essa aprovacao nao autoriza publicacao, uso de dados reais, integracoes reais, SaaS ou merge automatico do PR no 10.

## Checklist

| Area | Condicao | Status |
| --- | --- | --- |
| Banco | PostgreSQL gerenciado via `DATABASE_URL` | PENDENTE |
| Migrations | Cadeia PostgreSQL com bootstrap, dry-run e apply unitario formal | PENDENTE |
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
| Preview Vercel | Branches de preparacao para dados reais sem preview publico com configuracao real | PENDENTE |
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

## Politica De Preview

Branches de preparacao para dados reais nao podem gerar preview publico com configuracoes reais. Qualquer preview existente deve permanecer no maximo em `APP_MODE=demo`, com dados ficticios, sem banco real, sem credenciais reais, sem WhatsApp real e sem dados pessoais.

Para a branch `feature/real-data-readiness-2026-07-12`, o deploy automatico foi bloqueado em `frontend/vercel.json`. Previews ja criados antes da regra devem ser removidos ou cancelados manualmente em Vercel > projeto `crm` > Deployments.

## Proxima Aprovacao Necessaria

Antes de dados reais: provisionar secrets reais em cofre/provedor, aplicar migrations em PostgreSQL gerenciado, validar backup/restore externo, rodar auditoria final e obter aprovacao explicita do dono para uso real e publicacao.

## Supabase Vazio

Para projeto Supabase sem tabelas no schema `public`, a primeira migration PostgreSQL deve ser `2026_07_01_000_postgres_bootstrap_schema.sql`. Ela cria somente o schema base vazio usado pelo CRM e deve rodar antes das migrations aditivas de preparacao, sessoes e readiness.

O workflow `Supabase Migrations Dry Run` deve falhar se a bootstrap estiver ausente, fora de ordem, se houver `ALTER TABLE` em tabela inexistente para schema vazio ou se alguma migration contiver operacao destrutiva conhecida.

## Apply Unitario Supabase

O workflow `Supabase Migration Single Apply` e o caminho controlado para aplicar migrations no Supabase. Ele roda apenas manualmente, usa somente `SUPABASE_DIRECT_URL` como secret, exige confirmacao `APLICAR-MIGRATION`, bloqueia ordem incorreta, bloqueia reaplicacao, registra checksum em `schema_migrations`, faz teste transacional antes do apply e aplica somente uma migration por execucao.

Mesmo com esse workflow, dados reais continuam proibidos ate auditoria final, backup/restore aceito, credenciais seguras, validação LGPD e aprovacao explicita do dono.

## Auditoria Readonly Supabase

O workflow `Supabase Readonly Audit` deve ser executado depois das migrations e antes de qualquer configuracao de chaves de producao. Ele usa transacao `READ ONLY`, bloqueia comandos de escrita, nao aplica migrations, nao insere dados, nao imprime credenciais e publica apenas um relatorio seguro em job summary e artifact.

A decisao do relatorio readonly nao autoriza dados reais automaticamente. Ela apenas informa se o banco pode seguir para a proxima etapa de configuracao segura.

## Permissoes Supabase

Para USO PROPRIO, o backend deve ser o unico caminho autorizado para acessar dados. O workflow `Supabase Permissions Audit` deve ser executado para confirmar grants de `public`, `anon`, `authenticated`, `service_role` e `postgres`, estado de RLS e policies.

A recomendacao padrao deste projeto e `A) BACKEND-ONLY`: remover acessos diretos de `public`, `anon` e `authenticated` em tarefa futura aprovada. `B) RLS OBRIGATORIO` so deve ser escolhido se uma decisao futura exigir frontend acessando Supabase diretamente.
