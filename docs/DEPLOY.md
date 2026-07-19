# Deploy

## Status
Deploy controlado/teste online validado. Producao real com dados de clientes continua bloqueada.

## Tentativa de go-live real - 2026-07-18

Status: bloqueado com seguranca antes de qualquer merge, migration real, deploy ou habilitacao de dados reais.

- Checkpoints criados: `safety/pre-go-live-pr32-2026-07-18`, `pre-go-live-pr32-2026-07-18` e `safety/pr32-before-final-go-live-2026-07-18`.
- PR #32 validado localmente: backend 194 testes, frontend build/audit OK e E2E 2 aprovados com 1 skip controlado.
- Supabase principal validado por leitura: PostgreSQL 17.6, SSL ligado, `public` vazio e advisors sem lints.
- Vercel autenticado confirmou preview do PR #32 pronto e producao ainda na `main` anterior.
- Go-live segue bloqueado ate configurar Render, Resend, GitHub Actions secrets, backup pre-migration criptografado e restore descartavel.

Atualizacao tecnica do PR #32: foi preparado o workflow `PostgreSQL Backup and Restore Validation` para aprovar restore em PostgreSQL 17 descartavel no GitHub Actions, sem usar Supabase principal, secrets reais, dados reais ou ferramentas instaladas no computador local. Mesmo com esse teste aprovado, a ativacao real continua bloqueada ate DNS/Resend, secrets dos paineis, conexao controlada Render-Supabase e autorizacao final.

## Homologacao controlada pos-merge - 2026-07-18

Status: validado para uso restrito com dados ficticios.

- PR mergeado: #30.
- Hash antigo da `main`: `78b03f44552740e8e9364dc664afabe147c0d951`.
- Hash novo da `main`: `17a79f970f4721625f8143c47192c67425ec85e5`.
- Checkpoint de seguranca: branch `safety/pre-homologacao-pr-30-2026-07-18` e tag `pre-homologacao-pr-30-2026-07-18`.
- Frontend Vercel: `https://crm-sepia-beta.vercel.app` respondeu 200.
- Backend Render: `https://crm-2340.onrender.com/healthz` respondeu 200 com `{"status":"ok","service":"BBB Consig CRM API"}`.
- Smoke seguro: CORS permitido para o frontend, login/logout com usuario demo ficticio aprovados.

Validacoes locais pos-merge:
- Backend completo: 181 testes aprovados.
- Backup/restore ficticio e normalizacao/configuracao: 79 testes aprovados.
- Frontend: `npm audit --audit-level=moderate` sem vulnerabilidades e `npm run build` aprovado.
- E2E: aprovado, com ativacao admin ignorada quando `ADMIN_ACTIVATION_LINK` nao esta configurado.

Limites preservados: nenhum dado real, nenhuma migration real, nenhuma restauracao real, nenhuma integracao real e nenhum novo backup real foram executados.

## Preparacao para producao real USO_PROPRIO - 2026-07-18

Nao publicar automaticamente esta preparacao. O Render nao deve ser redeployado para dados reais e o Vercel nao deve receber configuracao real enquanto `REAL_DATA_MODE=false`.

Separacao esperada:
- Desenvolvimento/testes locais: SQLite local, dados ficticios, `APP_MODE=demo`.
- Homologacao publicada: PostgreSQL gerenciado quando `APP_ENV=production`; dados ficticios e integracoes simuladas enquanto `REAL_DATA_MODE=false`.
- Producao preparada: PostgreSQL gerenciado, secrets em painel seguro, `REAL_DATA_MODE=false` ate aprovacao final.

Variaveis por metadados, sem valores:
- Render/producao preparada: `APP_ENV`, `APP_MODE`, `PYTHON_VERSION`, `BBB_AUTH_SECRET`, `BBB_DATA_ENCRYPTION_KEY`, `CORS_ORIGINS`, `DATABASE_URL`, `DB_POOL_SIZE`, `DB_MAX_OVERFLOW`, `DB_POOL_RECYCLE_SECONDS`, `DB_POOL_TIMEOUT_SECONDS`, `REAL_DATA_MODE`, `EVOLUTION_API_MODE`, `APP_VERSION`, `AUTH_EMAIL_ENABLED`, `AUTH_EMAIL_MODE`, `AUTH_EMAIL_FROM`, `APP_PUBLIC_URL`, `RESEND_API_KEY`.
- GitHub Actions: `SUPABASE_DIRECT_URL`, `BACKUP_ENCRYPTION_KEY`, `POSTGRES_RESTORE_URL`.
- Vercel: `VITE_API_URL`, `VITE_APP_MODE`.
- Monitoramento: `MONITORING_ALERTS_ENABLED`, `MONITORING_CONTACT_CHANNEL`.

Efeito da ausencia:
- Sem `DATABASE_URL` PostgreSQL, producao real deve bloquear.
- Sem chave de criptografia, dados pessoais nao podem ser gravados.
- Sem backup configurado e restore isolado aprovado, ativacao real deve bloquear.
- Sem `CORS_ORIGINS` restrito ao frontend, API nao deve operar em modo real.

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
{"status":"ok","service":"BBB Consig CRM API","version":"0.1.0","database":"ok","environment":"demo"}
```

Login demo: validado com sucesso no ambiente Vercel.

## Retomada expressa de pre-publicacao - 2026-07-18

Estado verificado sem alterar provedores, secrets, banco ou workflow:

- Branch principal validada em `78b03f44552740e8e9364dc664afabe147c0d951`.
- Backend local: suite completa aprovada.
- Frontend: `npm ci`, `npm audit --audit-level=moderate` e `npm run build` aprovados.
- E2E local: fluxos principais aprovados; ativacao admin permanece ignorada quando `ADMIN_ACTIVATION_LINK` nao esta configurado.
- Backend Render: `/healthz` respondeu apos nova tentativa, comportamento compativel com cold start.
- Frontend Vercel: `/login` respondeu 200.
- Backup real criptografado existente foi confirmado por metadados do GitHub Actions; nenhum novo backup ou restore foi executado.

Essa verificacao sustenta aprovacao para publicacao controlada/homologacao com dados ficticios. Nao sustenta producao real com dados pessoais.

## Bloqueios atuais
- Autenticacao atual e adequada apenas para MVP controlado.
- Falta hardening completo de producao real.
- SQLite local nao e banco de producao e deve ser rejeitado em `APP_ENV=production`.
- Integracoes externas estao bloqueadas por design.
- Dados reais de clientes nao estao liberados.
- `APP_MODE` deve permanecer `demo`.

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
- `APP_MODE`
- `PYTHON_VERSION`
- `BBB_AUTH_SECRET`
- `CORS_ORIGINS`
- `DATABASE_URL`
- `DB_POOL_SIZE`
- `DB_MAX_OVERFLOW`
- `DB_POOL_RECYCLE_SECONDS`
- `DB_POOL_TIMEOUT_SECONDS`
- `REAL_DATA_MODE`
- `EVOLUTION_API_MODE`
- `AUTH_EMAIL_ENABLED`
- `AUTH_EMAIL_MODE`
- `AUTH_EMAIL_FROM`
- `APP_PUBLIC_URL`
- `RESEND_API_KEY`

`BBB_DATA_ENCRYPTION_KEY` e obrigatoria para `APP_MODE=production`/dados reais e recomendada para qualquer ensaio de hardening, mas nao e exigida pelo runtime demo controlado com `APP_MODE=demo` e `REAL_DATA_MODE=false`.

`AUTH_EMAIL_ENABLED=false` e `AUTH_EMAIL_MODE=simulate` devem permanecer ate o dominio/remetente do Resend estarem validados. `RESEND_API_KEY` nunca deve ser versionada ou colada no chat.

### Frontend Vercel
- `VITE_API_URL`

### Previews Vercel

Branches de preparacao para dados reais nao podem gerar preview publico com configuracoes reais.

O arquivo `frontend/vercel.json` bloqueia deploy automatico da branch `feature/real-data-readiness-2026-07-12`. Se a Vercel ja tiver criado um preview antes desta regra, remover/desativar manualmente no painel:
1. Abrir Vercel > projeto `crm` > Deployments.
2. Filtrar pela branch `feature/real-data-readiness-2026-07-12`.
3. Remover ou cancelar o deployment preview existente.
4. Confirmar que nenhum preview dessa branch usa `APP_MODE=production`, banco real, credenciais reais, WhatsApp real ou dados pessoais.

### Opcionais nesta fase
- `BACKEND_HOST`
- `BACKEND_PORT`
- `EVOLUTION_API_URL`
- `EVOLUTION_API_TOKEN`

`EVOLUTION_API_URL` e `EVOLUTION_API_TOKEN` devem ficar vazios enquanto WhatsApp estiver em modo simulacao.

`APP_MODE=demo` mantem o aviso de demonstracao, bloqueia CPF matematicamente valido em cadastros/simulacoes e impede que usuarios demo sejam tratados como operacao real.

Para `APP_MODE=production`, o backend deve bloquear a inicializacao se qualquer item de readiness estiver ausente: PostgreSQL, chave de criptografia, segredo de autenticacao forte, migrations aplicadas, backup configurado, consentimento obrigatorio, logs mascarados, HTTPS esperado e testes criticos aprovados.

## PostgreSQL para producao real

Producao real e qualquer backend publicado com `APP_ENV=production` exigem PostgreSQL gerenciado. SQLite permanece apenas para desenvolvimento e testes locais.

Para preparar PostgreSQL:
1. Criar um banco PostgreSQL gerenciado no provedor seguro escolhido.
2. Configurar a `DATABASE_URL` real somente no painel seguro do Render.
3. Nunca colar `DATABASE_URL` real no chat.
4. Nunca commitar `.env`.
5. Manter `REAL_DATA_MODE=false` ate concluir criptografia em repouso, autenticacao segura, backup/restore, monitoramento e revisao LGPD.
6. Confirmar SSL obrigatorio (`sslmode=require`) e pool compativel com o plano.
7. Apos configurar `DATABASE_URL`, redeployar o backend.

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

## Supabase PostgreSQL

Supabase foi escolhido como provedor PostgreSQL gerenciado para a etapa futura de producao real. Esta preparacao nao libera dados reais.

Na tela Connect/ORM do Supabase:
- `DATABASE_URL`: usar no Render para runtime da API. Preferir a conexao via shared transaction-mode pooler.
- `DIRECT_URL`: usar apenas para migrations/admin. Preferir a conexao via shared session-mode pooler.

As URLs podem vir com `[YOUR-PASSWORD]`. Substituir pela senha real somente no painel seguro do provedor ou em variavel local privada. Nunca colar senha no chat e nunca commitar `.env`.

Antes de apontar o Render para Supabase:
1. Criar o projeto Supabase.
2. Configurar `DIRECT_URL` apenas no ambiente seguro usado para migrations.
3. Rodar dry-run local: `python backend/scripts/apply_postgres_migrations.py`.
4. Aplicar migrations somente com aprovacao explicita: `python backend/scripts/apply_postgres_migrations.py --apply`.
5. Configurar `DATABASE_URL` no Render para runtime da API.
6. Manter `REAL_DATA_MODE=false`.
7. Testar `GET /healthz` e login demo com dados ficticios.

O script de migrations PostgreSQL usa `backend/migrations/postgres/*.sql`, exige `DIRECT_URL`, mascara a URL nos logs sem exibir usuario, host, senha ou path completo, e permanece bloqueado com `REAL_DATA_MODE=true`.

## Resend transacional

O CRM prepara envio transacional apenas para ativacao administrativa e recuperacao de senha.

Variaveis por nome:
- `AUTH_EMAIL_ENABLED`
- `AUTH_EMAIL_MODE`
- `AUTH_EMAIL_FROM`
- `APP_PUBLIC_URL`
- `RESEND_API_KEY`

Modo seguro padrao:
- `AUTH_EMAIL_ENABLED=false`
- `AUTH_EMAIL_MODE=simulate`

Para habilitar envio real, validar conta, dominio/remetente e chave no provedor. Nao usar para comunicacao comercial, WhatsApp, SMS ou clientes. Erros do provedor nao devem revelar se a conta existe.

## Dry-run Supabase via GitHub Actions

O projeto possui o workflow manual `Supabase Migrations Dry Run` para validar quais migrations PostgreSQL seriam aplicadas usando um Repository Secret. Esse fluxo nao aplica migrations e nao libera dados reais.

Para configurar:
1. Abrir o repositorio no GitHub.
2. Ir em `Settings`.
3. Ir em `Secrets and variables` -> `Actions`.
4. Criar um Repository secret:
   - Name: `SUPABASE_DIRECT_URL`
   - Value: `DIRECT_URL` do Supabase com a senha real.
5. Nunca colar essa URL no chat.
6. Ir em `Actions`.
7. Selecionar `Supabase Migrations Dry Run`.
8. Clicar em `Run workflow`.
9. Conferir nos logs se o workflow listou as migrations e se nenhuma migration foi aplicada.

Esse workflow:
- usa `SUPABASE_DIRECT_URL` apenas como secret do GitHub Actions;
- exporta o valor como `DIRECT_URL` para o script;
- executa `python backend/scripts/apply_postgres_migrations.py` sem `--apply`;
- mantem `REAL_DATA_MODE=false`;
- nao imprime usuario, host, senha ou URL completa;
- nao cria opcao de aplicar migration real.

## Aplicar migrations Supabase via GitHub Actions

Depois que o dry-run estiver com status `success`, existe um workflow manual separado para aplicar as migrations PostgreSQL no Supabase.

Para aplicar:
1. Confirmar que `Supabase Migrations Dry Run` passou com sucesso.
2. Abrir o repositorio no GitHub.
3. Ir em `Actions`.
4. Selecionar `Supabase Migrations Apply`.
5. Clicar em `Run workflow`.
6. No campo `confirmacao`, digitar exatamente:
   `APLICAR_MIGRATIONS_SUPABASE`
7. Executar o workflow.
8. Conferir os logs sem expor segredo.
9. Confirmar quais migrations foram aplicadas.

Esse fluxo altera a estrutura do banco PostgreSQL. Ele usa `SUPABASE_DIRECT_URL` somente como Repository Secret, exporta o valor como `DIRECT_URL` apenas durante o job, mantem `REAL_DATA_MODE=false` e executa `python backend/scripts/apply_postgres_migrations.py --apply`.

Esse fluxo nao publica a aplicacao, nao configura Render, nao insere seed de dados reais e nao libera uso com dados reais. Dados reais continuam proibidos ate concluir criptografia em repouso, autenticacao segura, backup/restore, monitoramento e revisao LGPD.

### Erro Invalid IPv6 URL no dry-run

Se o dry-run falhar com mensagem segura sobre `DIRECT_URL invalida`, normalmente a `DIRECT_URL` ainda contem `[YOUR-PASSWORD]` ou a senha possui caracteres reservados que quebram a URL.

Corrija o Repository Secret `SUPABASE_DIRECT_URL` no GitHub. Substitua `[YOUR-PASSWORD]` pela senha real somente no secret, nunca no chat. Se a senha tiver caracteres como `@`, `:`, `/`, `#`, `?`, `[` ou `]`, use uma senha forte com letras e numeros sem caracteres reservados ou aplique URL encoding na senha.

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
4. Se o primeiro acesso demorar ou expirar, repetir uma vez antes de classificar como fora do ar. O comportamento pode indicar cold start/latencia do plano, sem autorizar mudanca de infraestrutura.

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

## Reversao controlada

Se a publicacao controlada falhar:

1. Nao inserir dados reais.
2. Restaurar no provedor o ultimo deploy estavel da `main` validada.
3. Manter `APP_MODE=demo`, `REAL_DATA_MODE=false` e `EVOLUTION_API_MODE=simulation`.
4. Conferir `GET /healthz` no backend e `/login` no frontend.
5. Registrar o incidente sem incluir secrets, URL real de banco ou dados pessoais.
