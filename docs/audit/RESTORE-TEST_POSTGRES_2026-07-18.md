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

## RPO/RTO

- RPO esperado: ate o ultimo dado sintetico criado antes do `pg_dump`.
- RTO observado: medido pelo workflow como duracao de restore somada a validacao funcional.

## Procedimento

1. Rodar o workflow `PostgreSQL Backup and Restore Validation` no PR #32.
2. Confirmar status final `success`.
3. Conferir o job summary sem expor logs sensiveis.
4. Manter bloqueados merge, Render, Supabase real e dados reais ate as demais pendencias externas.

Nunca usar o Supabase principal como destino do restore.
