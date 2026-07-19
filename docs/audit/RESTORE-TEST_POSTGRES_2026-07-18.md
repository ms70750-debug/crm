# Restore Test PostgreSQL - 2026-07-18

## Status

Workflow de restore descartavel PostgreSQL 17 preparado para aprovacao no GitHub Actions. O Supabase principal foi validado por leitura anteriormente, mas nenhum banco real foi alterado nesta sessao.

## Escopo aprovado

O teste deve usar somente banco PostgreSQL descartavel e isolado, com dados sinteticos. Nunca restaurar sobre banco principal, homologacao atual ou banco com dados reais.

## Plano validado localmente

1. Aplicar migrations PostgreSQL em banco isolado.
2. Criar usuario administrador sintetico.
3. Criar token de ativacao e validar uso unico.
4. Login/logout sintetico.
5. Solicitar recuperacao sintetica.
6. Gerar backup criptografado.
7. Validar checksum.
8. Restaurar em segundo banco isolado.
9. Validar tabelas, indices, usuarios, tokens, sessoes, consentimentos e audit log.
10. Validar login apos restore.
11. Limpar ambientes descartaveis.

## Resultado atualizado em 2026-07-18

- Supabase localizado: sim, por conector autenticado.
- Projeto principal confirmado: `crm-bbb-consig-prod`.
- PostgreSQL: 17.6, saudavel, SSL ligado.
- Schema `public`: vazio antes das migrations da aplicacao.
- Advisors: sem lints retornados pelo conector.
- Ambiente de restore escolhido: GitHub Actions com PostgreSQL 17 descartavel.
- Workflow preparado: `.github/workflows/postgres-restore-validation.yml`.
- Dados sinteticos: administrador, usuario, cliente, consentimento, simulacao, audit log, token de ativacao/recuperacao e soft delete.
- Backup: `pg_dump` 17 em formato custom, checksum SHA-256 e criptografia Fernet com chave efemera do job.
- Restore: segundo banco descartavel com `pg_restore` 17 e validacao funcional do backend.
- Projeto criado: nao nesta tarefa.
- Plano pago criado: nao.
- Migration real aplicada: nao.
- Backup real executado: nao.
- Restore real executado: nao.
- Dados reais usados: nao.
- Motivo do bloqueio anterior: ambiente local sem `psql`/`pg_dump`/`pg_restore`/Docker disponivel e conector Supabase sem recurso de backup/export criptografado ou restore descartavel sem custo/confirmacao externa.
- Mitigacao: validacao deslocada para GitHub Actions, sem depender do computador local e sem tocar no Supabase principal.

## Correcao pg_dump PR #32 - 2026-07-18

### Diagnostico

- Run analisado: `29662203443`.
- Etapa com falha: `Create encrypted backup`.
- Codigo de saida: `1`.
- PostgreSQL descartavel: saudavel em `127.0.0.1:5432`.
- Servidor: PostgreSQL 17.10.
- Cliente anterior: `pg_dump` 17.10 em shim Docker `postgres:17`.
- Banco de origem: `crm_restore_source`.
- Evidencia sanitizada: `PGDUMP_INVALID_DATABASE_OBJECT`, arquivo de dump criado, dump vazio, criptografia nao iniciada, restore nao iniciado.
- Causa raiz classificada: J/I - shim Docker/argumentos. O cliente era executado fora do runner e dependia de uma connection string inteira propagada por `PGDATABASE`, o que podia ser interpretado como nome de banco/objeto invalido e deixava o dump vazio.

### Correcao

- Modelo escolhido: Modelo A - cliente PostgreSQL 17 no runner.
- Shims removidos: `pg_dump` e `pg_restore` em `.ci-bin`.
- Cliente final: `postgresql-client-17` instalado via repositório PGDG controlado.
- Execucao final: `psql`, `pg_isready`, `pg_dump` e `pg_restore` direto no runner, acessando o service container por `127.0.0.1` e porta `5432`.
- Helper final: scripts convertem a URL SQLAlchemy para variaveis libpq separadas, sem connection string em argumento.
- Teste de regressao: unitarios garantem que o workflow nao usa shims/Docker e que `pg_dump` recebe `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE` e `PGSSLMODE` separados.

### Limites

- Nenhum Supabase principal foi usado.
- Nenhum dado real foi usado.
- Nenhum backup real foi executado.
- Nenhum restore real foi executado.
- Nenhum artifact aberto deve ser publicado.

## Fixacao dos clientes PostgreSQL 17 PR #32 - 2026-07-18

### Diagnostico

- Run analisado: `29668273614`.
- Etapa com falha: `PostgreSQL client preflight`.
- Falha ocorreu antes do backup, antes da criptografia e antes do restore.
- Servidor descartavel: PostgreSQL 17.10.
- `psql` resolvido: 17.10.
- `pg_dump` resolvido pelo nome generico: 16.14.
- `pg_restore` resolvido pelo nome generico: 16.14.
- Causa raiz: resolucao de PATH/wrapper no runner Ubuntu, nao conexao, migrations ou dados sinteticos.

### Correcao

- `PG17_BIN` passa a ser descoberto por `dpkg -L postgresql-client-17`.
- Os caminhos reais sao validados com `readlink -f` e devem resolver dentro de `PG17_BIN`.
- Operacoes criticas usam caminhos absolutos:
  - `${PG17_BIN}/psql`;
  - `${PG17_BIN}/pg_isready`;
  - `${PG17_BIN}/pg_dump`;
  - `${PG17_BIN}/pg_restore`.
- O workflow adiciona `PG17_BIN` ao `PATH` somente como apoio, sem depender de wrapper generico ou `update-alternatives`.
- Os scripts de backup/restore aceitam `PG_DUMP_BIN` e `PG_RESTORE_BIN` para executar os binarios fixados.

### Limites preservados

- Nenhum Supabase principal foi alterado.
- Nenhum backup real foi executado.
- Nenhum restore real foi executado.
- Nenhum dado pessoal foi usado.
- Nenhum secret real foi registrado.

## RPO/RTO

- RPO esperado: ate o ultimo dado sintetico criado antes do `pg_dump`.
- RTO observado: medido pelo workflow como duracao de restore somada a validacao funcional.

## Procedimento

1. Rodar o workflow `PostgreSQL Backup and Restore Validation` no PR #32.
2. Confirmar status final `success`.
3. Conferir o job summary sem expor logs sensiveis.
4. Manter bloqueados merge, Render, Supabase real e dados reais ate as demais pendencias externas.

Nunca usar o Supabase principal como destino do restore.

## Correcao schema public PR #32 - 2026-07-19

### Diagnostico

- Run analisado: `29668607431`.
- Etapa com falha: `Validate checksum and restore`.
- Falha ocorreu depois de `pg_dump`, checksum, criptografia e remocao do dump aberto passarem.
- Clientes PostgreSQL: `psql`, `pg_dump`, `pg_restore` e `pg_isready` 17.10.
- Banco de origem anterior: `crm_restore_source`.
- Banco de destino anterior: `crm_restore_target`.
- Causa raiz confirmada: o dump custom inclui o comando de criacao do schema `public`, enquanto o banco de destino recem-criado ja continha `public`, comportamento padrao do PostgreSQL.
- Evidencia sanitizada: falha no `CREATE SCHEMA public` com schema preexistente.

### Correcao

- O workflow agora usa bancos sinteticos `crm_source_ci` e `crm_restore_ci`, criados a partir de `template0` com owner `restore_ci_owner`.
- Antes do restore, o script inspeciona o dump com `pg_restore --list` e registra apenas resumo seguro:
  - schema `public` incluido: sim/nao;
  - total de entradas;
  - presenca de tabelas;
  - presenca de indices;
  - presenca de constraints.
- O restore e bloqueado antes de qualquer `DROP` se:
  - o host nao for `127.0.0.1` ou `localhost`;
  - o banco de destino nao terminar em `_restore_ci` ou `_restore_test`;
  - o destino for `postgres`, `template0`, `template1`, `crm`, `crm_prod` ou `crm-bbb-consig-prod`;
  - origem e destino forem iguais;
  - houver referencia externa proibida a Supabase, Render, Vercel ou dominio real;
  - `SELECT current_database()` nao confirmar o destino esperado;
  - ja existirem tabelas da aplicacao no destino.
- Somente depois dessas protecoes, o script executa `DROP SCHEMA IF EXISTS public CASCADE` no banco descartavel aprovado.
- O schema `public` nao e recriado manualmente antes do restore; o dump deve recria-lo.

### Testes de regressao

- Host externo bloqueado antes do DROP.
- Nome de banco nao sintetico bloqueado.
- Origem igual ao destino bloqueada.
- Tabela da aplicacao preexistente bloqueia o DROP.
- Indice do dump confirma `SCHEMA - public`, tabelas, indices e constraints sem imprimir o indice completo.
- Workflow estatico confirma `template0`, `restore_ci_owner`, `crm_source_ci` e `crm_restore_ci`.

### Limites preservados

- Nenhum Supabase principal foi alterado.
- Nenhum Render, Vercel, Resend ou DNS foi alterado.
- Nenhum dado real, secret real, merge ou publicacao foi executado.
- O resultado final depende de uma nova execucao unica no GitHub Actions.

## Correcao datetime UTC PR #32 - 2026-07-19

### Diagnostico

- Run analisado: `29702441131`.
- Etapa com falha: `Validate backend against restored database`.
- Etapas aprovadas antes da falha: PostgreSQL 17, migrations, dados sinteticos, backup, checksum, criptografia, remocao do dump aberto, preparo do destino, restore e schema `public`.
- Arquivo: `backend/app/services/security.py`.
- Funcao: `_active_session_from_payload`.
- Comparacao anterior: `session.expires_at < datetime.utcnow()`.
- Valor aware: `session.expires_at`, carregado de `auth_sessions.expires_at` no PostgreSQL restaurado.
- Valor naive: `datetime.utcnow()`.
- Tipo SQL PostgreSQL: `TIMESTAMPTZ`.
- Tipo SQLite local: `DATETIME`, podendo retornar datetime naive.
- Causa classificada: H, mistura de B (`datetime.utcnow()` naive) e D (`TIMESTAMPTZ` retornando aware), com compatibilidade G para SQLite naive interno.

### Regra UTC

- Timezone canonico: UTC.
- Relogio atual: helper centralizado com `datetime.now(UTC)`.
- Valores aware: convertidos para UTC com `astimezone`.
- Valores naive internos: interpretados como UTC somente no contrato interno do CRM/SQLAlchemy.
- Valores ausentes ou invalidos: operacao rejeitada.
- Expiracao: `expires_at <= agora` expira; somente futuro e valido.
- Validacoes preservadas: sessao revogada, token usado, finalidade cruzada e usuario inativo continuam rejeitados.

### Correcao

- Criado helper `backend/app/services/datetime_utc.py`.
- Corrigidas comparacoes em sessoes, ativacao administrativa e recuperacao de senha.
- Nenhum endpoint, schema ou migration foi alterado.
- Testes novos cobrem UTC aware, offset diferente, naive interno, futuro, passado, limite exato, ausente, invalido e ausencia do TypeError original.

### Resultado esperado

A proxima execucao unica deve chegar na validacao funcional do backend restaurado sem `TypeError` de datetime naive/aware, preservando login, logout, ativacao, recuperacao, invalidacao de sessao, consentimento, audit log, simulacoes e soft delete.
