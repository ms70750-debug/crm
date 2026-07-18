# Backup E Restauracao

Status: ADR 012 APROVADO para USO PROPRIO. Backup real criptografado validado no GitHub Actions em artifact protegido; restauracao real continua proibida sem ambiente isolado e aprovacao explicita.

Ultima verificacao por metadados em 2026-07-18:

- Workflow: `Supabase Encrypted Backup`.
- Run ID: `29636132186`.
- Acionamento: `schedule`.
- Branch/commit: `main` em `78b03f44552740e8e9364dc664afabe147c0d951`.
- Resultado: sucesso.
- Artifact: `supabase-encrypted-backup`.
- Retencao efetiva: 7 dias, com expiracao indicada em `2026-07-25T07:40:49Z`.
- Classificacao: valido por metadados; nao houve download, descriptografia ou restore real.

## Politica minima para uso proprio real

- Frequencia: diaria.
- Criptografia: antes de qualquer upload.
- Checksum: obrigatorio para pacote criptografado e manifesto.
- Retencao: diaria minima de 7 dias, com recomendacao de copias semanais/mensais conforme capacidade.
- Duplicidade: workflow com concurrency sem cancelamento para evitar sobreposicao.
- Artifact: nunca incluir `.sql`, `.tar` ou dump aberto.
- Logs: secrets mascarados e erros sanitizados.
- Restore: somente em banco isolado ate autorizacao formal.

## Recuperacao

1. Confirmar incidente e congelar alteracoes quando necessario.
2. Selecionar backup criptografado aprovado.
3. Validar checksum.
4. Restaurar primeiro em banco isolado.
5. Validar tabelas, constraints, indices, login sintetico, cliente ficticio, audit log e soft delete.
6. Solicitar autorizacao explicita antes de qualquer restauracao no banco principal.

## Escopo Atual

O projeto possui scripts auxiliares para backup/restauracao ficticia local, usados em testes automatizados com banco temporario, e workflow operacional de backup criptografado do Supabase via CLI oficial.

A aprovacao do ADR nao autoriza restauracao real, publicacao real ou armazenamento externo fora do GitHub Actions. Uso real depende de auditoria final, credenciais seguras, provedor configurado e aprovacao explicita do dono.

## Requisitos Para Piloto Real

- Backup diario no provedor gerenciado.
- Retencao aprovada pelo dono.
- Backup criptografado.
- Verificacao de integridade por checksum.
- Teste de restauracao antes da ativacao.
- Alerta de falha.
- Separacao entre demo e producao.

## Procedimento Ficticio Local

1. Criar banco SQLite temporario com dados ficticios.
2. Executar `create_sqlite_backup`.
3. Executar `restore_sqlite_backup`.
4. Validar checksum e leitura dos dados ficticios.

## Reversao

Se restore falhar em ambiente real futuro, manter sistema bloqueado para dados reais, restaurar a partir do ultimo backup integro e registrar incidente.

## Supabase Plano Free

No plano Free, se snapshot/backup automatico nao estiver disponivel, a aplicacao de migrations deve ser precedida por inventario seguro do schema vazio e plano de rollback operacional. A aplicacao deve usar o workflow `Supabase Migration Single Apply`, uma migration por execucao manual.

Rollback automatico so ocorre dentro da transacao da migration em caso de erro durante o job. Rollback operacional com comandos de remocao de objetos so pode ser considerado enquanto nao houver dados reais e depois de falha comprovada, revisao do estado do banco e aprovacao explicita.

## Backup Externo Criptografado

Status: ADR 014 APROVADA para USO PROPRIO e ADR 009 aceita para o metodo operacional com Supabase CLI.

O fluxo ativo usa o Supabase CLI oficial para gerar tres arquivos logicos temporarios: `roles.sql`, `schema.sql` e `data.sql`. O arquivo de dados usa `--data-only` e `--use-copy`. O script empacota esses arquivos com manifesto e checksums internos, criptografa o pacote com Fernet e publica somente artifact criptografado, manifesto externo sanitizado e checksum externo.

### Escopo do dump Supabase CLI

O backup criptografado usa o schema `public`, que e o schema usado pelas migrations e modelos do CRM. O Supabase CLI aplica filtros especificos para o ambiente Supabase, evitando schemas internos e papeis reservados que causavam falhas no `pg_dump` bruto.

O artifact final contem somente:

- `crm-supabase-backup.tar.enc`;
- `crm-supabase-backup.manifest.json`;
- `crm-supabase-backup.sha256`.

Nao devem ser enviados como artifact:

- `roles.sql`;
- `schema.sql`;
- `data.sql`;
- pacote `.tar` aberto;
- dump bruto;
- logs com conteudo SQL.

Variaveis futuras:

- `SUPABASE_DIRECT_URL`: apenas como GitHub Actions secret.
- `BACKUP_ENCRYPTION_KEY`: apenas como GitHub Actions secret.
- `BACKUP_STORAGE_PROVIDER`: placeholder; armazenamento externo real ainda nao configurado.
- `BACKUP_STORAGE_BUCKET`: placeholder; bucket real ainda nao configurado.

### Backup automatico diario

O workflow `Supabase Encrypted Backup` roda automaticamente todos os dias as 06:00 UTC, equivalente a 03:00 no horario de Brasilia. A execucao automatica fica limitada a branch `main`, sem gatilho por pull request e sem gatilho por push.

Controles ativos:

- Supabase CLI oficial para roles, schema e dados;
- artifact somente com `.tar.enc`, manifesto sanitizado e `.sha256`;
- nenhum SQL aberto publicado;
- nenhum secret em argumento de linha de comando;
- concurrency unica para impedir duas rotinas simultaneas;
- retencao do GitHub Actions em 7 dias.

### Criar backup manual futuro

1. Confirmar aprovacao explicita para backup manual.
2. Configurar `BACKUP_ENCRYPTION_KEY` como secret seguro do GitHub Actions.
3. Confirmar que `SUPABASE_DIRECT_URL` existe somente como secret.
4. Executar manualmente `Supabase Encrypted Backup`.
5. Informar a confirmacao `CRIAR-BACKUP-CRIPTOGRAFADO`.
6. Baixar o artifact criptografado, quando aprovado, e armazenar em cofre/armazenamento externo aprovado.

O workflow automatico nao faz upload externo nesta fase.

### Restauracao documentada

1. Validar o checksum externo do `crm-supabase-backup.tar.enc`.
2. Descriptografar o pacote em diretorio temporario isolado.
3. Validar `checksums.txt` contra `roles.sql`, `schema.sql`, `data.sql` e `manifest.json`.
4. Restaurar `roles.sql`.
5. Restaurar `schema.sql`.
6. Restaurar `data.sql`.
7. Usar transacao e parada no primeiro erro (`ON_ERROR_STOP`).
8. Validar `schema_migrations`.
9. Validar tabelas, indices, constraints e policies esperadas.
10. Validar contagens sem mostrar dados.
11. Validar login e dashboard em ambiente isolado.
12. Remover arquivos SQL e tar abertos.

Nunca restaurar sobre o Supabase real.

### Retencao proposta

- 7 backups diarios no GitHub Actions artifact.
- 4 semanais.
- 3 mensais.

Retencao semanal/mensal depende de armazenamento externo aprovado. Enquanto esse armazenamento nao existir, a retencao efetiva e de 7 dias no GitHub Actions.

### Chave e corrupcao

Troca de chave: criar nova chave em secret seguro, gerar novo backup, testar restore e manter chave antiga enquanto existirem backups antigos dentro da retencao.

Perda da chave: backups criptografados existentes devem ser considerados irrecuperaveis. O projeto deve permanecer bloqueado para dados reais ate existir novo backup validado.

Backup corrompido: qualquer divergencia de checksum bloqueia restore e exige novo backup.

### Armazenamento externo futuro

O provedor externo ainda nao foi escolhido nem configurado. Opcoes futuras devem ser avaliadas por custo, criptografia em repouso, controle de acesso, logs de auditoria, retencao e facilidade de restore.

## Proibicoes

- Nao versionar backup.
- Nao colar credenciais no chat.
- Nao testar restore com dados reais nesta etapa.
- Nao armazenar dump aberto como artifact permanente.
- Nao configurar armazenamento externo real sem nova aprovacao.
