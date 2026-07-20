# Changelog

## 2026-07-19 - Trava de destino Supabase oficial

### Adicionado
- Criada ADR do banco PostgreSQL oficial, definindo `crm-bbb-consig-prod` como destino canonico.
- Adicionada trava de fingerprint nao reversivel para bloquear backup, migrations, auditorias e bootstrap quando o destino divergir.
- Conectados os workflows Supabase e bootstrap administrativo ao secret `EXPECTED_DATABASE_TARGET_FINGERPRINT`.
- Criado relatorio de reconciliacao de destino sem identificadores, hosts ou conexoes.

### Mantido
- Render permanece em SQLite demo e `REAL_DATA_MODE=false`.
- Nenhum cliente foi criado, nenhum secret foi exibido e nenhuma migration foi aplicada no Supabase oficial nesta alteracao.

## 2026-07-19 - Sincronizacao da main no PR 32

### Alterado
- Sincronizada a `main` atual (`e626e7e`) na branch `release/preparar-producao-real-2026-07-18` por merge comum, sem rebase e sem force push.
- Incorporado o bootstrap de administrador principal por variaveis de ambiente da `main`, mantendo senha como valor externo (`sync: false`) e sem segredo no repositorio.
- Mantido o bloqueio do PR 32 contra SQLite em producao, com `DATABASE_URL` externo no Render e `REAL_DATA_MODE=false`.
- Preservado o visual BBB aprovado, a otimizacao de assets e o roteamento `/api` para login na preview de branch.

### Validado
- Conflitos resolvidos manualmente em `backend/tests/test_migration_strategy.py` e `render.yaml`.
- Teste focado de migrations/admin aprovado antes de concluir o merge.

### Mantido
- Nenhum merge na `main`, nenhuma publicacao em producao, nenhuma migration real, nenhum Supabase, Render/Vercel de producao, Resend, DNS, secret, e-mail real, administrador real ou dado real foi alterado nesta sincronizacao.

## 2026-07-19 - Login funcional na preview do PR 32

### Corrigido
- A preview de branch da Vercel passa a rotear chamadas de API por `/api` no mesmo dominio, evitando falha de fetch/CORS no navegador.
- Adicionada rewrite de `/api/(.*)` para o backend Render ja existente, antes do fallback do SPA.

### Mantido
- Nenhum backend, banco, migration, endpoint, autenticacao, permissao, Supabase, Render, Resend, DNS, secret, dado real, merge na main ou publicacao em producao foi alterado nesta correcao.

## 2026-07-19 - Otimizacao invisivel do visual BBB aprovado

### Alterado
- Otimizados os ativos locais do visual BBB sem alterar enquadramento, cores, textos ou estrutura aprovada.
- Adicionadas versoes WebP locais do banner em 1200px e 768px, mantendo o PNG original como fallback.
- Adicionada versao WebP local do logo para uso na UI, mantendo o JPEG original como fallback e favicon.
- Definidos `width` e `height` nos elementos de imagem de marca para reduzir risco de deslocamento de layout.
- Divididos chunks de vendor no Vite para separar React, Recharts, formularios e icones do chunk principal.
- Desabilitado inline de assets no build para manter imagens como arquivos estaticos rastreaveis.

### Medido
- Banner original: 540.81 kB.
- Banner WebP desktop: 31.13 kB.
- Banner WebP mobile: 16.95 kB.
- Logo original: 56.52 kB.
- Logo WebP UI: 1.61 kB.
- JavaScript principal: 758.96 kB antes; 230.37 kB depois, com vendors separados.
- CSS: 21.54 kB antes e depois.

### Mantido
- Visual aprovado pelo dono preservado.
- Nenhum backend, banco, migration, endpoint, autenticacao, permissao, Supabase, Render, Resend, DNS, secret, dado real, merge na main ou publicacao em producao foi alterado nesta otimizacao.

## 2026-07-19 - Identidade visual BBB no CRM

### Adicionado
- Criado design system visual BBB para o frontend, com tokens centralizados de cor, raio, sombra, tipografia e estados.
- Baixados localmente ativos oficiais servidos por `www.bbbemprestimos.com.br`: logo quadrada, banner institucional e favicon.
- Criado documento `docs/UI-DESIGN-SYSTEM.md` com referencia visual, paleta, componentes, responsividade, acessibilidade e limites.

### Alterado
- Redesenhadas visualmente telas de login, recuperacao de senha, redefinicao e ativacao administrativa com identidade BBB.
- Atualizados layout principal, menu lateral, navegacao movel, cabecalho, badges, botoes, inputs, paineis, tabelas e graficos para tema claro comercial.
- Corrigida rolagem horizontal geral em telas com tabelas largas, mantendo rolagem local controlada.

### Mantido
- Nenhum backend, banco, migration, endpoint, autenticacao, permissao, Supabase, Render, Resend, DNS, dado real, merge ou publicacao em producao foi alterado.

## 2026-07-19 - Datas UTC em validacoes de seguranca PR 32

### Corrigido
- Criado helper UTC canonico para comparacoes de seguranca, usando `datetime.now(UTC)` como relogio atual e normalizando valores internos para datetime timezone-aware em UTC.
- Corrigida a validacao de sessao em `backend/app/services/security.py`, evitando a comparacao entre `AuthSession.expires_at` aware vindo de PostgreSQL `TIMESTAMPTZ` e `datetime.utcnow()` naive.
- Corrigidas validacoes equivalentes de tokens de ativacao administrativa e recuperacao de senha em `backend/app/services/admin_bootstrap.py`.
- A regra de expiracao ficou explicita: `expires_at <= agora` expira; futuro permanece valido; data ausente ou invalida rejeita a operacao.
- Testes cobrem UTC aware, offset diferente, datetime naive interno interpretado como UTC, limite exato expirado, sessao restaurada, ativacao e recuperacao.

### Mantido
- Nenhum endpoint, contrato de resposta, schema, migration, Supabase, Render, Vercel, Resend, DNS, merge, publicacao, dado real ou secret real foi alterado.

## 2026-07-19 - Schema public preparado antes do restore PR 32

### Corrigido
- O restore criptografado agora inspeciona o indice do dump com `pg_restore --list` e confirma, sem imprimir o indice completo, que o dump inclui `SCHEMA - public`, tabelas, indices e constraints.
- O banco descartavel de destino passa a ser validado antes de qualquer `DROP`: host local, nome sintetico com sufixo `_restore_ci` ou `_restore_test`, origem diferente do destino, bancos proibidos bloqueados e ausencia de referencias externas proibidas.
- O script remove `DROP SCHEMA IF EXISTS public CASCADE` somente depois das protecoes passarem e somente no banco descartavel vazio, deixando o proprio dump recriar o schema `public`.
- O workflow cria bancos descartaveis via `template0`, com owner sintetico `restore_ci_owner`, usando `crm_source_ci` e `crm_restore_ci`.
- Testes de regressao cobrem bloqueio de host externo, nome de banco inseguro, origem igual ao destino, tabelas preexistentes antes do DROP e indice do dump com schema `public`.

### Mantido
- Nenhum Supabase principal, Render, Vercel, Resend, DNS, merge, publicacao, dado real ou secret real foi alterado.

## 2026-07-18 - Fixacao dos binarios PostgreSQL 17 no restore PR 32

### Corrigido
- O workflow `PostgreSQL Backup and Restore Validation` agora descobre `PG17_BIN` pelo pacote `postgresql-client-17` e chama `psql`, `pg_isready`, `pg_dump` e `pg_restore` por caminho absoluto.
- O preflight falha se qualquer binario critico nao existir, resolver fora de `PG17_BIN` ou retornar versao principal diferente de 17.
- Os scripts de backup e restore aceitam `PG_DUMP_BIN` e `PG_RESTORE_BIN`, permitindo que o workflow use exclusivamente os clientes PostgreSQL 17 fixados.
- Testes estaticos e unitarios passaram a barrar regressao para `pg_dump`/`pg_restore` genericos.

### Mantido
- Nenhum merge, publicacao, backup real, restore real, Supabase principal, Render, Vercel, Resend, DNS ou dado real foi alterado.

## 2026-07-18 - Correcao do pg_dump no restore descartavel PR 32

### Corrigido
- Removidos os shims Docker de `pg_dump` e `pg_restore` do workflow `PostgreSQL Backup and Restore Validation`.
- O workflow passa a instalar o cliente PostgreSQL 17 no runner e executar `psql`, `pg_isready`, `pg_dump` e `pg_restore` diretamente contra o service container local.
- O backup/restore agora separa a URL SQLAlchemy em variaveis libpq (`PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`, `PGSSLMODE`) antes de chamar ferramentas cliente, evitando passar connection string inteira como nome de banco.
- Adicionado preflight do cliente PostgreSQL antes do backup, validando versoes 17, disponibilidade, banco atual e diretorios de saida.

### Mantido
- Nenhum Supabase principal foi alterado, nenhum secret real foi usado, nenhuma publicacao ou merge foi executado, e os dados seguem sinteticos.

## 2026-07-18 - Restore descartavel PostgreSQL 17 no CI

### Adicionado
- Criado workflow `PostgreSQL Backup and Restore Validation` para PRs, usando PostgreSQL 17 descartavel no GitHub Actions.
- Adicionado script `backend/scripts/ci_postgres_restore_validation.py` para criar dados sinteticos e validar origem/restauracao sem Supabase, secrets reais ou dados pessoais.
- O workflow aplica as migrations oficiais, gera backup com `pg_dump` 17, calcula checksum, criptografa com chave efemera, remove o dump aberto, restaura com `pg_restore` 17 e valida o backend no banco restaurado.

### Corrigido
- O aplicador oficial PostgreSQL agora inclui as migrations recentes de primeiro admin e metadados de readiness, alem de registrar `checksum` e `applied_at` em `schema_migrations`.
- Scripts de backup/restore convertem `postgresql+psycopg://` para URL nativa apenas ao chamar ferramentas cliente PostgreSQL, mantendo SQLAlchemy no driver `psycopg`.

### Mantido
- Nenhum Supabase principal foi alterado, nenhum merge foi feito, nenhuma publicacao foi executada, nenhum secret real foi usado e `AUTH_EMAIL_MODE=simulate`/`REAL_DATA_MODE=false` permanecem obrigatorios.

## 2026-07-18 - Preparacao sem acesso a Locaweb

### Validado
- Criada e enviada a branch de seguranca `safety/pre-advance-without-dns-pr32-2026-07-18` apontando para o head atual do PR #32.
- PR #32 reconfirmado aberto, nao draft, mergeavel e com GitHub Action `PostgreSQL Backend Only Validation` aprovada.
- Supabase principal `crm-bbb-consig-prod` reconfirmado ativo, PostgreSQL 17.6, SSL ligado, schema `public` vazio e advisors sem lints.
- Frontend publico atual e backend `/healthz` responderam 200, sem alterar producao.
- Vercel autenticado confirmou preview do PR #32 em `READY` no commit atual.

### Preparado
- Checklist final atualizado para explicitar DNS na Locaweb, chave Resend restrita, backup pre-migration, restore descartavel, merge, Render com PostgreSQL, validacao Vercel, primeiro administrador e um unico e-mail de ativacao.
- Resend permanece validado apenas em modo `simulate`, com `AUTH_EMAIL_ENABLED=false`.

### Mantido
- Nenhum merge, nenhuma publicacao, nenhuma migration real, nenhum backup real, nenhum restore real, nenhum administrador real, nenhum e-mail real e nenhum dado real foram executados.

## 2026-07-18 - Tentativa segura de go-live do PR 32

### Validado
- Criados e enviados os checkpoints `safety/pre-go-live-pr32-2026-07-18`, `pre-go-live-pr32-2026-07-18` e `safety/pr32-before-final-go-live-2026-07-18`.
- PR #32 confirmado aberto, nao draft, mergeavel e com head `fd705e841d1ecc57f07417e626502fa1ce60fc23`.
- Backend completo aprovado com 194 testes, frontend aprovado com `npm ci`, `npm audit --audit-level=moderate` e build, E2E local aprovado com 2 testes e 1 skip controlado.
- Supabase principal `crm-bbb-consig-prod` confirmado ativo, PostgreSQL 17.6, SSL ligado, schema `public` vazio e advisors sem lints.
- Vercel autenticado confirmou preview do PR #32 pronto e producao ainda na `main` anterior.

### Bloqueado
- Go-live real nao foi executado porque backup pre-migration criptografado, restore descartavel, configuracao Render, validacao Resend e GitHub Actions secrets nao puderam ser concluidos com os acessos disponiveis nesta sessao.
- Nenhuma migration real foi aplicada, nenhum backup real foi criado, nenhum restore real foi executado, nenhum e-mail real foi enviado, nenhum administrador real foi criado, nenhum deploy foi acionado e `REAL_DATA_MODE` nao foi habilitado.

## 2026-07-18 - Integracao do PR 32 com autenticacao persistente

### Alterado
- Integrada a preparacao de producao real do PR 32 com a correcao de login/recuperacao do PR 33.
- Ambiente `APP_ENV=production` passa a exigir `DATABASE_URL` PostgreSQL, bloqueando SQLite local como fallback de producao.
- `render.yaml` deixa `DATABASE_URL` como secret externo e adiciona metadados de pool PostgreSQL e e-mail transacional.
- Adicionado servico de e-mail transacional Resend com `AUTH_EMAIL_MODE=simulate` por padrao para ativacao administrativa e recuperacao de senha.

### Mantido
- Nenhum Supabase real foi criado nesta sessao, nenhuma migration real foi aplicada, nenhum restore real foi executado, nenhum e-mail real foi enviado e `REAL_DATA_MODE=false` permanece obrigatorio.

## 2026-07-18 - Preparacao tecnica para producao real

### Adicionado
- Criado ADR `docs/adr/009-postgresql-producao-real.md` para formalizar PostgreSQL/Supabase como caminho de producao real em `USO_PROPRIO`.
- Adicionados metadados de readiness: versao de termo em consentimentos e versao/usuario tecnico em snapshots de simulacao.
- Adicionadas migrations aditivas `2026_07_18_production_readiness_metadata` para SQLite controlado e PostgreSQL, com rollback PostgreSQL.
- Criados `docs/MONITORING.md`, `docs/PRODUCTION-REAL-CHECKLIST.md` e `docs/audit/RESTORE-TEST_2026-07-18.md`.
- Atualizado `/healthz` para validar banco e expor somente metadados seguros.

### Mantido
- Dados reais, comunicacao real, publicacao, backup real, restore real e migrations em provedor continuam bloqueados ate aprovacao final.

## 2026-07-18 - Recuperacao segura de login e senha

### Corrigido
- Substituido o `mailto:` da tela de login por fluxo real de solicitacao e redefinicao de senha.
- Adicionados endpoints neutros `/auth/password-recovery/request`, `/auth/password-recovery/validate` e `/auth/password-recovery/confirm`.
- Separada a finalidade dos tokens de ativacao administrativa e recuperacao de senha para impedir uso cruzado.
- Redefinicao de senha passa a invalidar sessoes ativas e registrar auditoria sem token ou senha.

### Mantido
- Nenhum e-mail real e enviado pelo CRM, nenhum token aberto e persistido, nenhuma senha ou secret foi documentado e nenhuma publicacao foi realizada.

## 2026-07-18 - Homologacao controlada pos-merge do PR 30

### Validado
- Merge do PR #30 concluido na `main` em `17a79f970f4721625f8143c47192c67425ec85e5`, com checkpoint previo em `78b03f44552740e8e9364dc664afabe147c0d951`.
- Criados branch e tag de seguranca `safety/pre-homologacao-pr-30-2026-07-18` e `pre-homologacao-pr-30-2026-07-18`.
- Backend local, suite focada de backup/restore ficticio, build frontend, audit e E2E foram reexecutados apos o merge.
- Homologacao publica validada em `https://crm-sepia-beta.vercel.app` e `https://crm-2340.onrender.com/healthz`.

### Mantido
- Nenhum dado real foi usado, nenhuma migration real foi aplicada, nenhuma restauracao real foi executada, nenhum disparo real de integracao foi feito e nenhum novo backup real foi iniciado.

## 2026-07-18 - Preparacao expressa para publicacao controlada

### Documentado
- Registrada a retomada expressa de pre-publicacao com `main` validada no hash `78b03f44552740e8e9364dc664afabe147c0d951`.
- Esclarecido que o deploy controlado permanece em modo demo, com Render/Vercel ja documentados e sem liberacao para dados reais.
- Alinhada a documentacao de backup para deixar claro que o workflow ativo usa Supabase CLI, enquanto o preflight com `postgresql+psycopg://` permanece no script legado/testado.
- Registrado por metadados o backup criptografado automatico `Supabase Encrypted Backup` do run `29636132186`, sem download, restore ou exposicao de secrets.

### Mantido
- Nenhuma publicacao foi realizada, nenhum novo backup foi executado, nenhuma restauracao real foi executada, nenhuma migration real foi aplicada e nenhum secret foi alterado ou revelado.

## 2026-07-15 - Ativacao segura do primeiro administrador

### Adicionado
- Criado fluxo oficial de uso unico para ativacao do primeiro administrador real por link temporario.
- Adicionada tabela `admin_bootstrap_tokens` com somente hash do token, expiracao, uso unico e metadados auditaveis.
- Criados endpoints `/auth/admin-bootstrap/validate` e `/auth/admin-bootstrap/activate`.
- Criado workflow manual privado `Create First Admin` com artifact sensivel `admin-activation-link`.
- Criada pagina `/ativar-admin` para o proprietario definir a propria senha sem cadastro publico.
- Criada ADR 010 documentando riscos, expiracao, uso unico, auditoria e reversao.

### Mantido
- Login demo publico bloqueado, nenhum backup manual executado, nenhuma restauracao executada, nenhum secret revelado.

## 2026-07-15 - Liberacao segura para uso real

### Alterado
- Removidos da superficie publica os atalhos de login demo e avisos de ambiente demo quando `VITE_DEMO_MODE` nao estiver explicitamente habilitado.
- Bloqueado o endpoint `/auth/demo-login` por padrao, liberando demo apenas com `PUBLIC_DEMO_LOGIN_ENABLED=true` em ambiente nao produtivo.
- Ajustados os E2E para autenticar pelo formulario, sem botao de administrador demo.
- Agendado o workflow `Supabase Encrypted Backup` diariamente as 06:00 UTC apenas na `main`, mantendo acionamento manual com confirmacao.
- Aumentada a retencao do artifact criptografado do backup para 7 dias.

### Documentado
- Atualizados procedimento de backup/restauracao e ADR 009 com horario diario, escopo da `main`, retencao e proibicao de restore real.

### Mantido
- Nenhuma nova tentativa manual de backup foi executada, nenhuma restauracao foi executada, nenhum secret foi revelado e nenhuma publicacao foi realizada.

## 2026-07-15 - Backup oficial com Supabase CLI

### Alterado
- Substituido o fluxo ativo de backup criptografado por Supabase CLI oficial, separando roles, schema e dados.
- Adicionado pacote unico criptografado `crm-supabase-backup.tar.enc` com manifesto/checksums seguros.
- Criada ADR 009 documentando a decisao e o rollback por tag.

### Mantido
- Nenhum backup real foi executado, nenhuma restauracao foi executada, nenhum secret foi revelado e nenhuma publicacao foi realizada.

## 2026-07-15 - Escopo seguro do pg_dump de producao

### Corrigido
- Limitado o `pg_dump` criptografado ao schema `public`, comprovado como schema do CRM pelas migrations e modelos.
- Adicionado diagnostico sanitizado para SQLSTATE, tipo de objeto, schema e classe de erro sem imprimir stderr bruto.
- Documentado no manifesto os schemas gerenciados pelo Supabase excluidos do dump e as extensoes encontradas.

### Mantido
- Nenhum novo backup real foi executado, nenhuma restauracao foi executada, nenhum secret foi revelado e nenhuma publicacao foi realizada.

## 2026-07-15 - Saida vazia do pg_dump no backup

### Corrigido
- Validado o destino do dump antes do `pg_dump`, incluindo diretorio, escrita, espaco livre e caminho absoluto.
- Separada falha real do `pg_dump` de arquivo vazio, evitando mascarar erro de banco como `PGDUMP_OUTPUT_FILE_ERROR`.
- Bloqueada a continuidade para criptografia e upload quando o `pg_dump` termina sem gerar dump nao vazio.

### Mantido
- Nenhuma nova tentativa de backup foi executada, nenhuma restauracao foi executada, nenhum secret foi revelado e nenhuma publicacao foi realizada.

## 2026-07-15 - pg_dump 17 no workflow de backup

### Corrigido
- Ajustado o workflow `Supabase Encrypted Backup` para priorizar `/usr/lib/postgresql/17/bin` no `PATH` apos instalar `postgresql-client-17`, evitando que o runner use um `pg_dump` antigo no preflight.

### Mantido
- Nenhuma nova tentativa de backup foi executada, nenhuma restauracao foi executada, nenhum secret foi revelado e nenhuma publicacao foi realizada.

## 2026-07-15 - Diagnostico seguro complementar de pg_dump

### Adicionado
- Criados codigos internos `BACKUP_DIAGNOSTIC_CODE` para falhas de `pg_dump`, DNS, SSL, autenticacao, permissao, timeout, saida vazia e criptografia.
- Incluidas flags seguras sobre binario encontrado, arquivo de saida criado, arquivo nao vazio, criptografia iniciada e upload iniciado.
- Ampliados testes mockados para garantir que host, usuario, senha, URL e stderr bruto nao sejam exibidos nos diagnosticos.

### Mantido
- Nenhum backup real foi executado, nenhuma restauracao foi executada, nenhum secret foi revelado e nenhuma publicacao foi realizada.

## 2026-07-12 - Driver psycopg no preflight de backup

### Corrigido
- Normalizadas URLs PostgreSQL para `postgresql+psycopg://` em conexoes SQLAlchemy do preflight, evitando dependencia implicita de `psycopg2`.
- Mantido `pg_dump` recebendo a conexao por ambiente seguro, sem URL em argumentos e sem exposicao de host, usuario, senha ou chave.

### Mantido
- Nenhum backup real foi criado, nenhum Supabase real foi acessado, nenhum secret foi exposto e nenhuma publicacao foi realizada.

## 2026-07-12 - Diagnostico seguro de pg_dump

### Corrigido
- Ajustado backup criptografado para passar a conexao ao `pg_dump` por ambiente seguro em vez de argumento visivel.
- Adicionadas categorias seguras para falhas de `pg_dump`, sem stderr bruto e sem expor URL, host, usuario ou senha.
- Alinhado workflow `Supabase Encrypted Backup` para instalar cliente PostgreSQL compativel e registrar somente versoes principais e compatibilidade.

### Mantido
- Nenhum backup real foi criado, nenhum workflow real de backup/restore foi executado e o Supabase real nao foi alterado.

## 2026-07-12 - Backup externo criptografado

### Aprovado
- ADR 014 aprovada pelo dono do projeto para USO PROPRIO em 2026-07-12.
- Mantidas como pendentes a chave real, armazenamento externo, primeiro backup real, primeiro restore real controlado e agendamento.

### Adicionado
- Proposta a ADR 014 para backup externo criptografado com `pg_dump`, criptografia autenticada, checksum SHA-256 e restore testavel.
- Criados scripts `create_encrypted_postgres_backup.py` e `verify_encrypted_backup_restore.py` para backup criptografado e validacao de restore em PostgreSQL temporario.
- Criados workflows manuais `Supabase Encrypted Backup` e `PostgreSQL Backup Restore Test`, sem agendamento e sem upload externo real.
- Adicionados testes de criptografia, checksum, manifesto seguro, chave ausente/incorreta, artifact seguro, restore ficticio e workflows.

### Mantido
- Nenhum backup real foi criado, nenhum dado real foi usado, nenhuma credencial real foi configurada e nenhuma publicacao foi realizada.

## 2026-07-12 - Permissoes backend-only Supabase

### Adicionado
- Documentada a decisao `BACKEND-ONLY` para o Supabase: frontend sem CRUD direto, backend como unico caminho autorizado e `service_role` proibido no frontend.
- Criada migration PostgreSQL `2026_07_12_backend_only_permissions.sql` para revogar grants diretos de `PUBLIC`, `anon` e `authenticated` nas 12 tabelas do CRM.
- Criado rollback manual documentado para restaurar somente grants explicitamente controlados, mediante aprovacao futura.
- Criado workflow `PostgreSQL Backend Only Validation` com PostgreSQL 16 descartavel para validar cadeia de 5 migrations, bloqueio de grants, usuario `backend_app`, rollback e preservacao de dados ficticios.

### Mantido
- Nenhuma permissao real foi alterada nesta tarefa.
- Nenhuma migration foi aplicada no Supabase real, nenhum dado real foi usado e nenhuma publicacao foi realizada.

## 2026-07-12 - Auditoria de permissoes Supabase

### Adicionado
- Criado workflow manual `Supabase Permissions Audit` para auditar grants, owners, RLS, policies e roles sem alterar o banco.
- Criado script `backend/scripts/audit_supabase_permissions.py` para classificar tabelas como SEGURO, ATENCAO ou CRITICO e recomendar BACKEND-ONLY ou RLS OBRIGATORIO.
- Adicionados testes de classificacao para grants de `public`, `anon`, `authenticated`, tabelas sem RLS, mascaramento e estrategia backend-only.

### Mantido
- Nenhum GRANT, REVOKE, RLS, policy, migration, dado, credencial, deploy ou publicacao foi executado nesta tarefa.

## 2026-07-12 - Auditoria readonly Supabase

### Adicionado
- Criado workflow manual `Supabase Readonly Audit` para auditar o Supabase real sem aplicar migrations, DDL ou DML.
- Criado script `backend/scripts/audit_supabase_readonly.py` com transacao `READ ONLY`, bloqueio de comandos de escrita, relatorio seguro, job summary e artifact `supabase-readonly-audit`.
- Adicionados testes para validar bloqueio de escrita, mascaramento de erros, ausencia de segredos e relatorio apenas com metadados/contagens.

### Mantido
- Nenhum Supabase real acessado nesta tarefa, nenhuma migration aplicada, nenhum dado inserido, nenhum segredo exposto e nenhuma publicacao realizada.

## 2026-07-12 - Workflow unitario de apply Supabase

### Adicionado
- Criado workflow manual `Supabase Migration Single Apply` para aplicar somente uma migration PostgreSQL por execucao.
- Criado script `backend/scripts/apply_single_postgres_migration.py` com confirmacao explicita, controle de ordem, checksum, bloqueio de reaplicacao e teste transacional antes do apply.
- Adicionados testes para migration invalida, confirmacao invalida, ordem incorreta, reaplicacao, checksum divergente e erro com rollback transacional.

### Mantido
- Nenhuma migration real aplicada, nenhum Supabase real acessado, nenhum segredo exposto e nenhuma publicacao realizada.

## 2026-07-12 - Bootstrap PostgreSQL para Supabase vazio

### Adicionado
- Criada migration `backend/migrations/postgres/2026_07_01_000_postgres_bootstrap_schema.sql` para schema PostgreSQL inicial vazio.
- Documentado o schema base PostgreSQL em `docs/DATA-MODEL.md`.
- Reforcado o dry-run para validar cadeia em schema vazio antes de listar migrations.

### Mantido
- Nenhum Supabase real acessado, nenhuma migration real aplicada, nenhum dado real usado e nenhuma publicacao realizada.

## 2026-07-12 - Plano de conexao Supabase

### Adicionado
- Criado `docs/SUPABASE-CONNECTION-PLAN.md` com inventario de variaveis, migrations, GitHub Actions, backup, rollback e criterios para futura conexao controlada ao projeto Supabase.

### Mantido
- Nenhuma migration aplicada, nenhuma credencial real configurada, nenhuma publicacao realizada e dados reais continuam proibidos.

## 2026-07-12 - Correcao dos bloqueadores pre-merge do PR 10

### Corrigido
- Adicionada revogacao server-side de sessao no logout, com armazenamento de hash do identificador da sessao.
- Alinhados `docs/LGPD.md` e `docs/BACKUP-RESTORE.md` aos ADRs 009 a 013 aprovados para USO PROPRIO.
- Bloqueado deploy automatico da branch `feature/real-data-readiness-2026-07-12` no `frontend/vercel.json`.

### Mantido
- Dados reais, credenciais reais, WhatsApp real, PostgreSQL real e publicacao de producao continuam proibidos sem nova aprovacao explicita.

## 2026-07-12 - Aprovacao arquitetural para uso proprio

### Alterado
- ADRs 009 a 013 marcados como APROVADO pelo dono do projeto para escopo de USO PROPRIO.
- Registrado que a aprovacao dos ADRs nao autoriza dados reais, publicacao, integracoes reais, SaaS ou merge automatico do PR no 10.
- Mantida exigencia de auditoria final, credenciais seguras e aprovacao explicita antes de qualquer ativacao real.

## 2026-07-12 - Preparacao segura para dados reais

### Adicionado
- Propostos ADRs 009 a 013 para PostgreSQL, criptografia, autenticacao, backup/restauracao e retencao LGPD.
- Criada fundacao de readiness para bloquear `APP_MODE=production` sem controles obrigatorios.
- Adicionada camada isolada de protecao de dados com envelope versionado, autenticacao e hash separado de CPF.
- Criadas migrations aditivas para soft delete, campos protegidos, consentimento ampliado e auditoria de backup.
- Adicionados testes de criptografia, readiness, soft delete/restauracao, consentimento, migration temporaria e backup/restore ficticio.

### Bloqueios preservados
- `APP_MODE=demo` continua sendo o padrao seguro.
- Dados reais continuam proibidos ate auditoria final e aprovacao explicita.
- Nenhuma credencial real, conexao PostgreSQL real, publicacao ou merge foi realizado nesta preparacao.

## 2026-07-12 - Correcao documental do PR 9

### Corrigido
- Atualizado o relatorio de recuperacao para registrar o PR no 9 aberto.
- Atualizado o hash final revisado para `0f037840a576c5ac4f7e0350d3d89469ef6661e5`.
- Mantida a classificacao como MVP controlado para uso interno com dados ficticios.

## 2026-07-12 - Recuperacao segura pos-auditoria funcional

### Corrigido
- Adicionado `APP_MODE=demo` para manter o CRM em demonstracao controlada.
- Bloqueado CPF matematicamente valido em cadastros e simulacoes enquanto o modo demo estiver ativo.
- Reforcada sessao com cookie HttpOnly, SameSite adequado e Secure em producao.
- Criado logout auditado e login demo por perfil sem expor senha na tela.
- Mantida Evolution API em modo 100% simulado com status visivel.
- Adicionadas acoes seguras de status/exclusao em leads, propostas e tarefas conforme permissao.
- Adicionado opt-out de WhatsApp para consentimento.

### Testes
- Backend passou de 32 para 36 testes aprovados.
- E2E atualizado para validar login demo, aviso de ambiente, opt-in/opt-out, WhatsApp simulado, INSS simulado e Admin.
- Build frontend segue aprovado, com alerta conhecido de bundle acima de 500 kB.

### Bloqueios preservados
- Nao houve migracao para PostgreSQL.
- Nao houve publicacao em Render/Vercel.
- Nao houve liberacao para dados reais ou SaaS.
- Criptografia em repouso e multi-tenancy seguem bloqueados por ADR e decisao comercial.

## 2026-07-03 - Workflow controlado para aplicar migrations Supabase

### Adicionado
- Criado workflow manual separado para aplicacao das migrations PostgreSQL.
- Exigida confirmacao `APLICAR_MIGRATIONS_SUPABASE`.
- Mantido `REAL_DATA_MODE=false`.
- Mantida proibicao de dados reais.

## 2026-07-02 - Mascara reforcada da DIRECT_URL

### Corrigido
- Reforcada a mascara da DIRECT_URL para ocultar usuario e host completos.
- Mantida protecao contra vazamento de senha e URL completa.
- Mantido dry-run sem aplicacao de migrations.

## 2026-07-02 - Tratamento seguro de DIRECT_URL invalida

### Corrigido
- Corrigida falha segura quando `DIRECT_URL` contem placeholder ou formato invalido.
- Evitado traceback bruto com `urlsplit`.
- Mantida protecao contra vazamento de segredo.

## 2026-07-02 - Workflow dry-run Supabase

### Alterado
- Criado workflow manual de dry-run das migrations Supabase via GitHub Actions.
- Usado secret `SUPABASE_DIRECT_URL` sem expor senha.
- Mantida proibicao de dados reais.
- Nenhuma migration e aplicada por esse workflow.

## 2026-07-02 - Preparacao Supabase PostgreSQL

### Alterado
- Documentada configuracao Supabase PostgreSQL.
- Diferenciado `DATABASE_URL` para runtime e `DIRECT_URL` para migrations/admin.
- Preparado script seguro para dry-run/aplicacao manual de migrations PostgreSQL.
- Mantido bloqueio de dados reais e `REAL_DATA_MODE=false`.

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
