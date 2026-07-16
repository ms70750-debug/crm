# Backup E Restauracao

Status: ADR 012 APROVADO para USO PROPRIO. Nenhum backup real externo configurado nesta tarefa.

## Escopo Atual

O projeto possui somente scripts auxiliares para backup/restauracao ficticia local, usados em testes automatizados com banco temporario. Eles nao conectam em provedor real e nao manipulam dados pessoais reais.

A aprovacao do ADR nao autoriza dados reais, publicacao real ou backup externo de producao. Uso real depende de auditoria final, credenciais seguras, provedor configurado e aprovacao explicita do dono.

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

Status: ADR 014 PROPOSTO PARA APROVACAO. A fundacao tecnica existe, mas backup real externo ainda nao esta autorizado.

O fluxo proposto usa `pg_dump` em formato custom, criptografa o dump com Fernet antes de qualquer artifact, gera checksums SHA-256 e cria manifesto seguro sem URL, host, usuario, senha ou conteudo de cliente.

### Escopo do dump PostgreSQL

O backup criptografado exporta explicitamente o schema `public`, que e o schema usado pelas migrations e modelos do CRM. Esse escopo inclui a estrutura e os dados das tabelas do CRM, sequences, indices, constraints, funcoes, triggers, policies RLS e objetos proprios existentes em `public` que sejam exportaveis pelo usuario de backup.

Schemas gerenciados pelo Supabase, como `auth`, `storage`, `vault`, `realtime` e `extensions`, nao sao exportados como parte do dump logico do CRM. Eles devem ser recriados pelo provedor ou por configuracao administrativa controlada do ambiente, e o manifesto do backup registra os schemas excluidos e as extensoes encontradas para apoiar uma restauracao isolada.

Se `pg_dump` falhar por permissao em tabela, sequence ou schema essencial do CRM, o backup deve falhar com diagnostico sanitizado. Essa falha nao deve ser mascarada por exclusao de objeto essencial.

Variaveis futuras:

- `SUPABASE_DIRECT_URL`: apenas como GitHub Actions secret.
- `BACKUP_ENCRYPTION_KEY`: apenas como GitHub Actions secret.
- `BACKUP_STORAGE_PROVIDER`: placeholder; armazenamento externo real ainda nao configurado.
- `BACKUP_STORAGE_BUCKET`: placeholder; bucket real ainda nao configurado.

### Criar backup manual futuro

1. Confirmar aprovacao explicita para backup real.
2. Configurar `BACKUP_ENCRYPTION_KEY` como secret seguro do GitHub Actions.
3. Confirmar que `SUPABASE_DIRECT_URL` existe somente como secret.
4. Executar manualmente `Supabase Encrypted Backup`.
5. Informar a confirmacao `CRIAR-BACKUP-CRIPTOGRAFADO`.
6. Baixar o artifact criptografado, quando aprovado, e armazenar em cofre/armazenamento externo aprovado.

O workflow nao e agendado e nao faz upload externo nesta fase.

### Testar restauracao

1. Executar manualmente `PostgreSQL Backup Restore Test`.
2. Informar o `artifact_run_id` do backup criptografado.
3. Informar a confirmacao `TESTAR-RESTAURACAO`.
4. O workflow restaura somente em PostgreSQL 16 temporario.
5. Validar tabelas, migrations, indices, constraints, contagens e permissoes BACKEND-ONLY.
6. Conferir o manifesto para extensoes e schemas gerenciados que precisam existir ou ser recriados no ambiente isolado.

Nunca restaurar sobre o Supabase real.

### Retencao proposta

- 7 backups diarios.
- 4 semanais.
- 3 mensais.

Artifacts do GitHub Actions devem ter retencao curta. Retencao real depende de armazenamento externo aprovado.

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
- Nao agendar backup sem aprovacao explicita.
- Nao configurar armazenamento externo real sem nova aprovacao.
