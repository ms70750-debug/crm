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
