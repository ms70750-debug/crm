# Restore Test PostgreSQL - 2026-07-18

## Status

Bloqueado com seguranca para restore real. O Supabase principal foi validado por leitura, mas nenhum banco foi alterado nesta sessao.

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
- Projeto criado: nao nesta tarefa.
- Plano pago criado: nao.
- Migration real aplicada: nao.
- Backup real executado: nao.
- Restore real executado: nao.
- Dados reais usados: nao.
- Motivo do bloqueio: ambiente local sem `psql`/`pg_dump`/`pg_restore`/Docker disponivel e conector Supabase sem recurso de backup/export criptografado ou restore descartavel sem custo/confirmacao externa.

## RPO/RTO

- RPO observado: nao medido sem banco isolado externo.
- RTO observado: nao medido sem banco isolado externo.

## Acao manual inevitavel

Disponibilizar execucao segura do workflow `PostgreSQL Backup Restore Test` com artifact de backup criptografado valido, `BACKUP_ENCRYPTION_KEY` em secret store e PostgreSQL temporario do CI. Nunca usar o Supabase principal como destino do restore.
