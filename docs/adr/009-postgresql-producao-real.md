# ADR 009 - PostgreSQL para producao real USO_PROPRIO

## Status
Proposto para aprovacao final. Preparacao tecnica permitida; ativacao com dados reais permanece bloqueada.

## Data
2026-07-18

## Contexto
O CRM BBB CONSIG esta homologado como `USO_PROPRIO - MVP CONTROLADO`, com SQLite em ambiente de demonstracao e dados ficticios. O uso real por correspondente e equipe interna exige banco gerenciado, backup/restore testado, seguranca, LGPD tecnica, monitoramento e autorizacao explicita do dono.

## Situacao atual com SQLite
SQLite permanece adequado para desenvolvimento e testes locais. Ele nao e adequado para ambiente publicado com `APP_ENV=production`, mesmo com `REAL_DATA_MODE=false`, porque autenticacao, tokens e sessoes administrativas precisam persistir entre cold starts e deployments.

## Necessidade de PostgreSQL gerenciado
PostgreSQL gerenciado e necessario para confiabilidade operacional, isolamento de credenciais, backup externo, controle de conexoes, SSL, migrations formais e rollback por snapshot.

## Provedor selecionado
Supabase PostgreSQL, por ja estar previsto na documentacao, nos workflows e nos scripts existentes. Nenhum novo provedor foi escolhido.

## Alternativas consideradas
- Manter SQLite: rejeitado para dados pessoais.
- Render PostgreSQL: viavel, mas exigiria nova decisao de provedor.
- Supabase PostgreSQL: escolhido por compatibilidade ja preparada.

## Decisao
Preparar PostgreSQL/Supabase como banco alvo de producao real, mantendo `REAL_DATA_MODE=false` ate a autorizacao final. Migrations devem ser aplicadas somente por fluxo formal, com URL direta em secret seguro e sem seed de demonstracao.

Ambiente `APP_ENV=production` deve falhar com seguranca se `DATABASE_URL` nao for PostgreSQL. A aplicacao normaliza PostgreSQL para `postgresql+psycopg://`, exige SSL e usa pool controlado.

## Impacto
- Producao real passa a depender de `DATABASE_URL` PostgreSQL no backend.
- Homologacao publicada futura com `APP_ENV=production` tambem depende de PostgreSQL persistente.
- Migrations PostgreSQL ficam em `backend/migrations/postgres`.
- Dados demo nao sao migrados automaticamente.
- Frontend continua consumindo somente a API do backend.

## Riscos
- Custo/plano do provedor pode exigir acao manual.
- Criacao de projeto pode exigir senha, 2FA ou aprovacao de conta.
- Aplicar migrations no banco errado pode causar indisponibilidade; por isso o apply real continua manual e confirmado.

## Custos conhecidos
Nao foi criado plano pago nesta tarefa. Custos dependem do plano Supabase/Render/Vercel selecionado pelo dono.

## Estrategia de migracao
1. Criar/provisionar projeto Supabase correto.
2. Configurar secrets no GitHub/Render sem revelar valores.
3. Rodar dry-run em banco vazio.
4. Aplicar migrations PostgreSQL formais.
5. Validar schema, indices, constraints, audit log e consentimento.
6. Executar backup criptografado.
7. Executar restore em banco isolado.
8. Somente depois pedir autorizacao final para dados reais.

## Estrategia de reversao
- Antes da ativacao real: manter homologacao atual em SQLite/demo.
- Depois de apply em banco vazio: descartar banco isolado se falhar.
- Depois da ativacao real futura: restaurar snapshot/backup validado e voltar `REAL_DATA_MODE=false`.

## Criterios para ativacao
- PostgreSQL criado e identificado como projeto correto.
- Migrations aplicadas em ambiente isolado e depois no alvo correto.
- Restore isolado aprovado.
- `BBB_DATA_ENCRYPTION_KEY`, `BBB_AUTH_SECRET` e `BACKUP_ENCRYPTION_KEY` em cofre/env seguro.
- `MIGRATIONS_APPLIED`, `BACKUP_CONFIGURED`, `CONSENT_REQUIRED`, `LOGS_MASKED`, `HTTPS_EXPECTED` e `CRITICAL_TESTS_APPROVED` verdadeiros.
- Revisao juridica das minutas LGPD.
- Autorizacao final explicita do dono.

## Criterios para voltar ao SQLite
SQLite so pode ser usado novamente para demo, treinamento, teste ou contingencia sem dados reais. Se qualquer dado real tiver entrado no PostgreSQL, nao copiar esse conteudo para SQLite local.

## Politica de backup
Backup diario criptografado antes do upload, checksum obrigatorio, retencao minima documentada e nenhum SQL aberto como artifact. Falha de backup deve bloquear ativacao real.

## Politica de restauracao
Restore nunca deve ocorrer sobre banco principal sem plano aprovado. Testes devem restaurar em banco isolado, vazio e descartavel.

## Protecao de dados pessoais
CPF deve ter hash deterministico para busca e valor criptografado separado. Conta, agencia, endereco e campos sensiveis futuros devem usar criptografia em repouso, logs mascarados, soft delete, trilha de auditoria e retencao documentada.
