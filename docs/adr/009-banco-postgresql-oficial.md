# ADR 009 - Banco PostgreSQL oficial

Status: aceito

Classificacao: USO_PROPRIO

## Contexto

Durante a preparacao do cutover foi identificado que o destino lido pelo secret do GitHub Actions nao correspondia ao estado observado no projeto Supabase conectado ao Codex. O banco apontado pelo secret continha schema operacional e registros tecnicos, enquanto o projeto conectado ao Codex estava com o schema `public` vazio.

## Decisao

O banco oficial do BBB Consig CRM e o projeto Supabase conectado ao Codex, identificado pelo nome operacional `crm-bbb-consig-prod`.

Nao deve ser criado segundo projeto Supabase para este CRM. Qualquer destino diferente deve ser classificado como destino anterior nao verificado, preservado somente leitura, sem novas migrations, sem exclusao e sem ser usado pelo Render.

## Regras

- Migrations, backups, auditorias, readiness e cutover nao podem confiar apenas no nome do secret.
- Todo workflow que usa conexao real deve validar a identidade do destino antes de acessar o banco.
- A validacao deve usar uma fingerprint nao reversivel configurada como secret externo.
- A connection string, host, usuario, senha, project ref, token e hash de senha nao devem ser registrados.
- O Render so pode ser alterado depois de backup oficial aprovado, migrations aplicadas no projeto oficial e bootstrap validado.
- Resend real fica fora do escopo desta decisao e deve permanecer em modo simulado.

## Backup

O projeto oficial deve ter backup criptografado proprio antes de qualquer migration, mesmo quando estiver vazio. Backups de destinos anteriores nao substituem backup do projeto oficial.

## Rollback

Antes de alterar o Render, registrar o deployment SQLite atual, manter `REAL_DATA_MODE=false` e documentar o retorno para a configuracao anterior. Nenhum restore deve ser executado no banco principal durante o rollback.

## Revisao futura

Esta ADR deve ser revisada se houver troca de provedor, branch database, pooler, usuario de conexao, politica de SSL, estrategia de backup ou requisito de multi-tenant.
