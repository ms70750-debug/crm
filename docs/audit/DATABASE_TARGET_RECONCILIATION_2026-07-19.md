# Reconciliacao De Destino PostgreSQL - 2026-07-19

## Resumo

O destino oficial definido pelo dono e o projeto Supabase conectado ao Codex: `crm-bbb-consig-prod`.

O destino anteriormente usado pelo GitHub Secret foi classificado como nao verificado ate que seja provado ser o mesmo projeto fisico. Ele deve permanecer somente leitura, com o backup criptografado ja preservado, sem novas migrations e sem uso pelo Render.

## Estado confirmado

- Banco do GitHub Secret: estrutura existente, sem usuarios e sem dados comerciais, com registros tecnicos de bootstrap/auditoria.
- Banco conectado ao Codex: schema `public` vazio no momento da reconciliacao.
- Backup do destino anterior: preservado no GitHub Actions run `29709499365`.
- Auditoria do destino anterior: registrada no run `29709600631`.
- Render: permanece em SQLite demo.
- Dados reais: nao liberados.

## Decisao operacional

Como os estados observados divergem, o cutover fica bloqueado ate que os secrets sejam rotacionados para o projeto oficial e a nova trava aprove o destino.

## Protecao adicionada

Foi criado um verificador de destino que:

- normaliza a conexao em memoria;
- calcula fingerprint SHA-256 nao reversivel;
- compara contra `EXPECTED_DATABASE_TARGET_FINGERPRINT`;
- falha antes de backup, migration, auditoria ou bootstrap quando `DATABASE_TARGET_GUARD_REQUIRED=true`;
- mascara explicitamente conexao e fingerprint nos workflows controlados de migrations;
- retorna apenas `destino aprovado` ou `destino divergente`.

## Acao manual segura

Uma acao pessoal sera necessaria para autorizar no painel seguro a atualizacao dos secrets para o projeto oficial. Nenhum valor deve ser enviado pelo chat.
