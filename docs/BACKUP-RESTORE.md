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

## Proibicoes

- Nao versionar backup.
- Nao colar credenciais no chat.
- Nao testar restore com dados reais nesta etapa.
