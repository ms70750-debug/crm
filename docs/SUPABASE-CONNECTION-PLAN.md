# Supabase Connection Plan

Status: plano de conexao controlada. Nenhuma migration aplicada. Nenhuma credencial real configurada.

Projeto Supabase identificado pelo dono: Projeto ms70750-debug.

Classificacao do CRM: USO PROPRIO. Dados reais continuam proibidos ate auditoria final, backup/restore externo validado, credenciais seguras e aprovacao explicita do dono.

## Escopo

Este plano prepara a conexao futura do CRM BBB CONSIG com o projeto Supabase ja criado. Ele nao conecta banco real, nao aplica migrations, nao altera Render/Vercel, nao publica e nao solicita valores secretos no chat.

## Inventario Do Repositorio

| Item | Situacao encontrada | Observacao |
|---|---|---|
| `.env.example` | Possui `DATABASE_URL`, `DIRECT_URL`, flags de readiness e `REAL_DATA_MODE=false` | Nao contem valores reais |
| Runtime backend | Usa `DATABASE_URL` em `backend/app/database/session.py` | SQLite segue padrao local/controlado |
| Readiness | `backend/app/services/readiness.py` bloqueia `APP_MODE=production` sem controles obrigatorios | Inclui `DATABASE_URL`, chave de dados, auth secret, migrations, backup, consentimento, logs, HTTPS e testes |
| Script de migrations | `backend/scripts/apply_postgres_migrations.py` | Usa `DIRECT_URL`, mascara logs, bloqueia `REAL_DATA_MODE=true` |
| GitHub Actions | `Supabase Migrations Dry Run`, `Supabase Migrations Apply`, `Supabase Migration Single Apply` e `Supabase Readonly Audit` | Workflows manuais, com `SUPABASE_DIRECT_URL` como Repository Secret |
| Migrations PostgreSQL | `backend/migrations/postgres/*.sql` | Aditivas, com `IF NOT EXISTS`, sem `DROP` |
| Migrations SQLite/legadas | `backend/migrations/*.sql` e `backend/migrations/sqlite/*.sql` | Usadas para MVP local/controlado |
| Render | `render.yaml` ainda usa SQLite controlado | Nao alterar nesta tarefa |
| Vercel | `frontend/vercel.json` bloqueia preview da branch sensivel anterior | Nao alterar nesta tarefa |
| Docs existentes | `docs/ENVIRONMENT.md`, `docs/DEPLOY.md`, `docs/DATA-MODEL.md`, `docs/BACKUP-RESTORE.md` | Ja documentam Supabase, secrets e bloqueio de dados reais |
| Supabase client direto | Nao encontrado | Frontend nao usa `SUPABASE_URL` nem `SUPABASE_ANON_KEY` |
| Project ref | Nao encontrado no repositorio | Nao registrar project ref se nao for necessario |

## Variaveis Necessarias

### GitHub Actions

| Variavel | Finalidade | Onde configurar | Sensivel | Obrigatoria |
|---|---|---|---|---|
| `SUPABASE_DIRECT_URL` | Secret usado pelos workflows manuais de dry-run/aplicacao de migrations | GitHub > Repository > Settings > Secrets and variables > Actions | Sim | Sim para dry-run/apply futuro |
| `DIRECT_URL` | Nome usado pelo script durante o job, vindo de `SUPABASE_DIRECT_URL` | Somente no ambiente do workflow | Sim | Sim durante o job |
| `REAL_DATA_MODE` | Manter bloqueio de uso real durante migrations | Definido no workflow como `false` | Nao | Sim |

### Render

| Variavel | Finalidade | Onde configurar | Sensivel | Obrigatoria |
|---|---|---|---|---|
| `APP_ENV` | Ativar validacoes de ambiente | Render Environment | Nao | Sim |
| `APP_MODE` | Manter modo controlado; padrao permitido segue `demo` | Render Environment | Nao | Sim |
| `PYTHON_VERSION` | Fixar runtime Python compativel | Render Environment/render.yaml | Nao | Sim |
| `BBB_AUTH_SECRET` | Assinatura de sessao | Render Environment | Sim | Sim |
| `BBB_DATA_ENCRYPTION_KEY` | Chave de protecao de dados pessoais futura | Render Environment | Sim | Sim antes de production real |
| `CORS_ORIGINS` | Origens autorizadas do frontend | Render Environment | Nao | Sim |
| `DATABASE_URL` | Runtime da API; usar pooler transaction-mode do Supabase no futuro | Render Environment | Sim | Sim para PostgreSQL futuro |
| `REAL_DATA_MODE` | Bloqueio de dados reais | Render Environment | Nao | Sim, manter `false` |
| `EVOLUTION_API_MODE` | Garantir WhatsApp simulado | Render Environment | Nao | Sim, manter `simulation` |
| `MIGRATIONS_APPLIED` | Readiness de migrations formais | Render Environment | Nao | Sim antes de `APP_MODE=production` |
| `BACKUP_CONFIGURED` | Readiness de backup externo | Render Environment | Nao | Sim antes de `APP_MODE=production` |
| `CONSENT_REQUIRED` | Readiness de consentimento obrigatorio | Render Environment | Nao | Sim antes de `APP_MODE=production` |
| `LOGS_MASKED` | Readiness de logs mascarados | Render Environment | Nao | Sim antes de `APP_MODE=production` |
| `HTTPS_EXPECTED` | Readiness de HTTPS | Render Environment | Nao | Sim antes de `APP_MODE=production` |
| `CRITICAL_TESTS_APPROVED` | Readiness de testes criticos | Render Environment | Nao | Sim antes de `APP_MODE=production` |

### Vercel

| Variavel | Finalidade | Onde configurar | Sensivel | Obrigatoria |
|---|---|---|---|---|
| `VITE_API_URL` | URL publica do backend | Vercel Project Settings > Environment Variables | Nao | Sim |
| `SUPABASE_URL` | Nao usada pelo app atual | Nao configurar nesta fase | Sim se usada futuramente | Nao |
| `SUPABASE_ANON_KEY` | Nao usada pelo app atual | Nao configurar nesta fase | Sim | Nao |
| `SUPABASE_SERVICE_ROLE_KEY` | Proibida no frontend | Nunca configurar na Vercel | Sim, alto risco | Nao |

### Ambiente Local

| Variavel | Finalidade | Onde configurar | Sensivel | Obrigatoria |
|---|---|---|---|---|
| `DATABASE_URL` | SQLite local ou PostgreSQL controlado privado para teste tecnico | `.env` local fora do Git | Sim se PostgreSQL | Nao para demo SQLite |
| `DIRECT_URL` | Dry-run local privado de migrations PostgreSQL | `.env` local fora do Git | Sim | Apenas para dry-run local |
| `BBB_AUTH_SECRET` | Sessao local | `.env` local fora do Git | Sim | Sim em execucao controlada |
| `BBB_DATA_ENCRYPTION_KEY` | Teste de criptografia local | `.env` local fora do Git | Sim | Sim para caminhos de protecao |
| `REAL_DATA_MODE` | Bloqueio de dados reais | `.env` local | Nao | Sim, manter `false` |

### Supabase

| Variavel | Finalidade | Onde configurar | Sensivel | Obrigatoria |
|---|---|---|---|---|
| `DATABASE_URL` | String de conexao runtime via pooler transaction-mode | Copiar do painel Supabase para Render, quando aprovado | Sim | Sim para runtime PostgreSQL futuro |
| `DIRECT_URL` | String de conexao admin/migrations via pooler session-mode | Copiar do painel Supabase para GitHub Secret, quando aprovado | Sim | Sim para dry-run/apply futuro |
| Database password | Senha das connection strings | Painel Supabase e secrets seguros | Sim | Sim |
| Backups | Backup gerenciado do projeto | Supabase Dashboard | Sim operacional | Sim antes de primeira migration real |
| `SUPABASE_URL` | API URL do Supabase | Nao usada pelo app atual | Sim operacional | Nao |
| `SUPABASE_ANON_KEY` | Chave publica anon | Nao usada pelo app atual | Sim operacional | Nao |
| `SUPABASE_SERVICE_ROLE_KEY` | Chave administrativa | Nao usar no CRM nesta fase | Sim, alto risco | Nao |

## Migrations

### Migrations Encontradas

Legado SQLite/local:
- `backend/migrations/2026_06_30_initial_schema.sql`
- `backend/migrations/2026_07_01_auth_etapa_3.sql`
- `backend/migrations/2026_07_01_leads_etapa_2.sql`
- `backend/migrations/2026_07_01_fundacao_seguranca_lgpd.sql`

SQLite controlado:
- `backend/migrations/sqlite/2026_07_02_postgres_preparacao.sql`
- `backend/migrations/sqlite/2026_07_12_auth_sessions.sql`
- `backend/migrations/sqlite/2026_07_12_real_data_readiness.sql`

PostgreSQL/Supabase:
- `backend/migrations/postgres/2026_07_01_000_postgres_bootstrap_schema.sql`
- `backend/migrations/postgres/2026_07_02_postgres_preparacao.sql`
- `backend/migrations/postgres/2026_07_12_auth_sessions.sql`
- `backend/migrations/postgres/2026_07_12_real_data_readiness.sql`

### Ordem Recomendada

O script atual carrega somente `backend/migrations/postgres/*.sql` em ordem lexicografica. Para Supabase vazio, a ordem segura e:

1. `2026_07_01_000_postgres_bootstrap_schema.sql`
2. `2026_07_02_postgres_preparacao.sql`
3. `2026_07_12_auth_sessions.sql`
4. `2026_07_12_real_data_readiness.sql`

### Dependencias

As migrations PostgreSQL de preparacao, sessoes e readiness sao aditivas e dependem das tabelas base ja existirem: `leads`, `clientes`, `propostas`, `tarefas`, `whatsapp_messages`, `users`, `audit_logs`, `consents` e `simulations`.

Como o projeto Supabase foi informado como sem migrations aplicadas, a migration bootstrap PostgreSQL passa a ser obrigatoria antes de qualquer apply real. Ela cria o schema base vazio, sem usuario demo, sem dados reais e sem secrets.

Sem essa migration base, o workflow `Supabase Migrations Apply` tende a falhar nas primeiras instrucoes `ALTER TABLE`.

### Compatibilidade PostgreSQL

As migrations em `backend/migrations/postgres` usam `TIMESTAMPTZ`, `SERIAL`, `IF NOT EXISTS` e nao possuem comandos destrutivos conhecidos. As migrations legadas da raiz usam `DATETIME` e `INTEGER PRIMARY KEY`; elas devem ser tratadas como referencia local/SQLite e nao aplicadas diretamente no Supabase sem conversao e revisao.

### Rollback

Nao ha migrations down formais. O rollback seguro para a primeira conexao deve ser operacional:

- backup/snapshot antes de qualquer migration;
- restauracao para snapshot em caso de falha;
- manter `DATABASE_URL` do Render apontando para SQLite/demo ate a validacao completa;
- nao ativar `APP_MODE=production`;
- nao ativar `REAL_DATA_MODE=true`.

### Riscos

- Banco Supabase vazio nao possui schema base exigido pelas migrations aditivas.
- Aplicar URL errada pode alterar banco errado.
- Usar `DATABASE_URL` no lugar de `DIRECT_URL` para migration pode misturar runtime e admin.
- Sem backup/restore testado, qualquer migration real fica bloqueada.
- Configurar `SUPABASE_SERVICE_ROLE_KEY` em Vercel ou frontend seria risco critico.
- Conectar Render ao PostgreSQL antes de migrations/readiness pode impedir startup ou expor ambiente incompleto.

### Testes Previos Necessarios

- `python -m pytest backend/tests`
- `npm run build`
- E2E local com dados ficticios
- `npm audit --audit-level=moderate`
- varredura de segredos no diff
- dry-run do workflow `Supabase Migrations Dry Run`
- validacao da cadeia PostgreSQL para schema vazio pelo script `backend/scripts/apply_postgres_migrations.py`
- teste de backup/restore do Supabase em projeto sem dados reais
- validacao manual de que logs nao imprimem connection strings

### Apply Unitario Recomendado

O caminho recomendado para aplicacao controlada no Supabase vazio e o workflow `Supabase Migration Single Apply`, que aplica somente uma migration por execucao manual. Ele exige:

- `migration`: uma das quatro migrations PostgreSQL aprovadas;
- `expected_previous_migration`: a migration imediatamente anterior esperada, ou `NONE` para a bootstrap;
- `confirmation`: valor exato `APLICAR-MIGRATION`.

O workflow faz validacao estatica, bloqueia operacoes destrutivas conhecidas, executa teste transacional quando tecnicamente possivel, aplica apenas o arquivo selecionado, registra `version`, `checksum` e `applied_at` em `schema_migrations`, bloqueia reaplicacao e impede checksum divergente.

Sequencia manual:

1. Rodar `Supabase Migrations Dry Run` no GitHub Actions.
2. Conferir que os logs listam migrations sem exibir URL, usuario, host, senha ou path completo.
3. Confirmar que `2026_07_01_000_postgres_bootstrap_schema.sql` aparece como primeira migration.
4. Ir em GitHub > Actions > `Supabase Migration Single Apply`.
5. Clicar em `Run workflow`.
6. Usar branch `main`.
7. Escolher a migration.
8. Informar a migration anterior esperada.
9. Digitar `APLICAR-MIGRATION`.
10. Executar e validar o resultado antes da proxima migration.

Ordem esperada:

| Etapa | Migration | `expected_previous_migration` |
|---|---|---|
| 1 | `2026_07_01_000_postgres_bootstrap_schema.sql` | `NONE` |
| 2 | `2026_07_02_postgres_preparacao.sql` | `2026_07_01_000_postgres_bootstrap_schema.sql` |
| 3 | `2026_07_12_auth_sessions.sql` | `2026_07_02_postgres_preparacao.sql` |
| 4 | `2026_07_12_real_data_readiness.sql` | `2026_07_12_auth_sessions.sql` |

O workflow antigo `Supabase Migrations Apply` permanece documentado como legado e nao deve ser usado para a aplicacao controlada uma-a-uma.

### Auditoria Readonly

Apos aplicar as migrations manualmente, a validacao do banco real deve usar o workflow `Supabase Readonly Audit`. Ele roda somente por `workflow_dispatch`, usa `SUPABASE_DIRECT_URL` apenas como secret do GitHub Actions, inicia transacao `BEGIN READ ONLY`, executa somente consultas `SELECT`, finaliza com `ROLLBACK` e publica um relatorio seguro no job summary e no artifact `supabase-readonly-audit`.

O workflow bloqueia comandos de escrita como `INSERT`, `UPDATE`, `DELETE`, `CREATE`, `ALTER`, `DROP`, `TRUNCATE`, `GRANT`, `REVOKE`, `COPY`, `CALL` e `DO`. O relatorio nao deve exibir URL, host, usuario, senha, CPF, email, telefone, dados bancarios, token ou hash completo de sessao.

Passos manuais:

1. Ir em GitHub > Actions.
2. Abrir `Supabase Readonly Audit`.
3. Clicar em `Run workflow`.
4. Usar branch `main`.
5. Aguardar o job concluir.
6. Abrir o job summary ou baixar o artifact `supabase-readonly-audit`.
7. Conferir divergencias, bloqueadores e decisao antes de qualquer proxima etapa.

## Conexao GitHub/Supabase

Classificacao: B) GitHub Actions e suficiente.

A conexao direta do repositorio ao Supabase e desnecessaria nesta fase. O caminho mais seguro para este projeto e manter Supabase sem reposititorio conectado, usar GitHub Actions manual com Repository Secret `SUPABASE_DIRECT_URL`, exigir dry-run, exigir confirmacao explicita para apply e manter `REAL_DATA_MODE=false`.

Conexao direta pode automatizar demais uma etapa que ainda exige auditoria, backup, schema base e aprovacao do dono. Portanto, nao conectar o repositorio diretamente ao Supabase agora.

## Plano De Backup

Antes da primeira migration real:
- confirmar que nao ha dados reais no projeto;
- criar backup/snapshot no Supabase Dashboard;
- registrar horario, responsavel e motivo;
- confirmar que backup nao contem segredos versionados;
- validar que restore esta disponivel para o projeto.

Apos migrations:
- criar novo backup/snapshot;
- registrar lista de migrations aplicadas;
- executar smoke test com dados ficticios;
- verificar integridade de tabelas e `schema_migrations`;
- manter `REAL_DATA_MODE=false`.

Teste de restore:
- restaurar em ambiente/projeto de teste, se disponivel;
- validar `/healthz`, login demo e consulta ficticia;
- comparar checksum/listagem de tabelas;
- documentar resultado antes de qualquer uso real.

Retencao:
- definir politica aprovada pelo dono;
- alinhar com LGPD;
- nao reter backup alem do necessario;
- restringir acesso a responsaveis autorizados.

Rollback:
- pausar uso online;
- nao apontar Render para banco com migration falha;
- restaurar snapshot anterior;
- confirmar schema;
- rodar testes com dados ficticios;
- registrar incidente e nova aprovacao antes de retentar.

## Acao Manual Do Dono

Supabase:
1. Abrir o projeto `Projeto ms70750-debug`.
2. Ir em Settings > Database.
3. Copiar a connection string de runtime via pooler transaction-mode somente para o painel seguro do Render quando autorizado.
4. Copiar a connection string admin/session-mode somente para GitHub Repository Secret quando autorizado.
5. Verificar Backups e confirmar se o plano/projeto permite snapshot/restore antes da primeira migration.
6. Nao conectar o repositorio diretamente ao Supabase nesta etapa.

GitHub:
1. Abrir o repositorio.
2. Ir em Settings > Secrets and variables > Actions.
3. Criar ou atualizar apenas o Repository Secret `SUPABASE_DIRECT_URL`, quando houver aprovacao para dry-run.
4. Ir em Actions > Supabase Migrations Dry Run.
5. Rodar o workflow manual e conferir logs sem revelar segredo.
6. Ir em Actions > Supabase Migration Single Apply.
7. Rodar uma migration por vez, com `expected_previous_migration` correto e confirmacao `APLICAR-MIGRATION`.
8. Validar o resultado antes da proxima migration.
9. Apos as quatro migrations, rodar `Supabase Readonly Audit` e revisar o artifact seguro.

Render:
1. Nao alterar `DATABASE_URL` nesta etapa.
2. Quando aprovado, configurar `DATABASE_URL` do Supabase somente no painel seguro.
3. Manter `APP_MODE=demo` e `REAL_DATA_MODE=false`.
4. Nao redeployar para uso real sem nova aprovacao.

Vercel:
1. Nao adicionar variaveis Supabase nesta etapa.
2. Nao configurar `SUPABASE_SERVICE_ROLE_KEY`.
3. Manter preview publico sem configuracoes reais.

## Acao Do Codex

- Manter este plano versionado.
- Revisar dry-run logs quando o dono autorizar credenciais seguras fora do chat.
- Propor migration PostgreSQL inicial se o banco Supabase estiver vazio.
- Nao aplicar migrations sem nova autorizacao explicita.
- Nao pedir nem receber secrets pelo chat.

## Criterios Para Liberar Aplicacao Das Migrations

- PR deste plano aprovado.
- `SUPABASE_DIRECT_URL` configurado como GitHub Repository Secret, sem expor valor.
- Backup/snapshot Supabase confirmado.
- Restore testado ou procedimento de restore formalmente aceito.
- Schema base PostgreSQL aprovado e validado se o banco estiver vazio.
- Dry-run do GitHub Actions com sucesso.
- Workflow `Supabase Migration Single Apply` revisado e aprovado.
- Workflow `Supabase Readonly Audit` revisado e aprovado para auditoria pos-migration.
- Varredura de segredos limpa.
- Backend, frontend build e E2E com dados ficticios aprovados.
- Nova autorizacao explicita do dono para aplicar migrations.

## Estado Final Deste Plano

- Credenciais reais configuradas: nao.
- Migration aplicada: nao.
- Banco real conectado: nao.
- Publicacao realizada: nao.
- Dados reais utilizados: nao.
