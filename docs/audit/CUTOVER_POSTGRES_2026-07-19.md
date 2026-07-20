# Cutover PostgreSQL - 2026-07-19

## Atualizacao De Reconciliacao

O cutover PostgreSQL permanece bloqueado ate que o secret `SUPABASE_DIRECT_URL` e a fingerprint protegida apontem comprovadamente para o projeto oficial `crm-bbb-consig-prod`.

O destino anteriormente auditado pelo GitHub Actions fica preservado somente leitura. Ele nao deve receber novas migrations, nao deve ser usado pelo Render e nao deve substituir backup do projeto oficial.

## Estado

- Render: SQLite demo preservado.
- Projeto oficial conectado ao Codex: canonico.
- REAL_DATA_MODE: false.
- Resend real: desabilitado.
- Clientes criados pelo Codex: nao.
