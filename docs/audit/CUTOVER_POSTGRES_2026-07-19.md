# Cutover PostgreSQL - 2026-07-19

## Atualizacao De Reconciliacao

O cutover PostgreSQL permanece bloqueado ate que o secret `SUPABASE_DIRECT_URL` e a fingerprint protegida apontem comprovadamente para o projeto oficial `crm-bbb-consig-prod`.

O destino anteriormente auditado pelo GitHub Actions fica preservado somente leitura. Ele nao deve receber novas migrations, nao deve ser usado pelo Render e nao deve substituir backup do projeto oficial.

## Estado

- Render: variaveis de ambiente de producao controlada salvas sem deploy automatico.
- Projeto oficial conectado ao Codex: canonico e com PostgreSQL migrado.
- REAL_DATA_MODE: false.
- Resend real: desabilitado.
- Clientes criados pelo Codex: nao.

## Execucao Controlada - 2026-07-20 UTC

- Senha tecnica do PostgreSQL oficial redefinida pelo painel Supabase.
- Conexao PostgreSQL via pooler validada sem exposicao de URL, senha ou fingerprint.
- Secrets `SUPABASE_DIRECT_URL` e `EXPECTED_DATABASE_TARGET_FINGERPRINT` atualizados no GitHub Actions.
- Backup criptografado pre-migration executado com sucesso no workflow `Supabase Encrypted Backup`.
- Dry-run de migrations PostgreSQL executado com sucesso.
- Migrations PostgreSQL aplicadas com sucesso e reexecutadas com sucesso para confirmar idempotencia.
- Auditorias readonly e de permissoes executadas com sucesso apos migrations.
- Banco oficial validado sem leads, clientes ou dados demo.
- Administrador principal criado diretamente no banco oficial, totalizando exatamente 1 usuario e 1 admin ativo.
- Blueprint do Render atualizado para preservar `APP_MODE=production`, `REAL_DATA_MODE=true` e flags de prontidao no deploy final.
