# Restore Test PostgreSQL - 2026-07-18

## Status

Pendente por acesso externo. Nenhum banco Supabase foi criado ou alterado nesta sessao.

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

## Resultado desta tarefa

- Supabase localizado: nao, sem conector/acesso autenticado nesta sessao.
- Projeto criado: nao.
- Plano pago criado: nao.
- Migration real aplicada: nao.
- Backup real executado: nao.
- Restore real executado: nao.
- Dados reais usados: nao.

## RPO/RTO

- RPO observado: nao medido sem banco isolado externo.
- RTO observado: nao medido sem banco isolado externo.

## Acao manual inevitavel

Provisionar ou disponibilizar acesso seguro a um projeto Supabase PostgreSQL isolado, com `DIRECT_URL`/`POSTGRES_RESTORE_URL` em secret store, sem expor valores no chat ou no Git.
