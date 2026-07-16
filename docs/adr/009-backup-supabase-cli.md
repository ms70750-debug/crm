# ADR 009 - Backup oficial com Supabase CLI

Status: aceito

Data: 2026-07-15

## Contexto

O backup customizado baseado em `pg_dump` bruto falhou repetidamente em objetos gerenciados pelo Supabase, mesmo depois de ajustes de driver, versao do cliente, caminho de arquivo, escopo `public`, `--no-owner` e `--no-privileges`.

O uso direto de `pg_dump` continua vulneravel a detalhes internos do ambiente gerenciado. A documentacao oficial do Supabase recomenda o Supabase CLI para dumps logicos porque ele aplica filtros especificos do ambiente Supabase.

## Decisao

Usar o Supabase CLI para separar o backup em tres partes logicas:

1. roles;
2. schema;
3. data com `--data-only` e `--use-copy`.

Esses arquivos ficam apenas em diretorio temporario, sao empacotados localmente, criptografados e removidos antes do upload. O artifact publico do workflow contem somente pacote criptografado, manifesto externo sanitizado e checksum externo.

## Alternativas Consideradas

- Continuar remendando `pg_dump` bruto: rejeitado porque ja falhou apos varias correcoes seguras e ainda depende de detalhes internos do Supabase.
- Backup nativo do painel: rejeitado para este fluxo porque nao gera o artifact criptografado e versionado pelo processo operacional do projeto.
- Supabase CLI: aceito porque e o metodo oficial suportado para dumps logicos com filtros de Supabase.

## Consequencias

- Tres arquivos logicos temporarios sao criados: `roles.sql`, `schema.sql` e `data.sql`.
- Um unico pacote temporario e montado antes da criptografia.
- O artifact contem somente `crm-supabase-backup.tar.enc`, manifesto externo e checksum externo.
- A restauracao passa a ser em etapas: roles, schema e data.
- O runner do GitHub Actions passa a depender do Supabase CLI instalado via npm.
- O workflow passa a ter execucao diaria as 06:00 UTC somente na `main`, mantendo `workflow_dispatch` com confirmacao manual.
- A retencao do artifact no GitHub Actions passa a ser 7 dias.

## Plano de Reversao

A tag `pre-merge-supabase-cli-backup-2026-07-15` preserva a `main` anterior ao merge desta decisao. O script legado baseado em `pg_dump` permanece no repositorio para referencia e rollback controlado, mas o workflow principal nao deve executa-lo.

## Criterios de Revisao

- Nenhum secret, URL, host, usuario, senha, token ou chave aparece em logs, manifesto ou artifacts.
- Nenhum SQL aberto e enviado como artifact.
- Falha em roles, schema ou data interrompe o processo.
- Temporarios sao removidos em sucesso ou falha.
- Testes cobrem CLI ausente, falhas por etapa, pacote incompleto, criptografia, checksums, manifesto sanitizado e ordem ficticia de restauracao.
- Testes cobrem o gatilho diario, bloqueio de PR/push, execucao apenas na `main` e retencao de 7 dias.
