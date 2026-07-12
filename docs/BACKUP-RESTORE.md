# Backup E Restauracao

Status: PROPOSTO PARA APROVACAO. Nenhum backup real configurado nesta tarefa.

## Escopo Atual

O projeto possui somente scripts auxiliares para backup/restauracao ficticia local, usados em testes automatizados com banco temporario. Eles nao conectam em provedor real e nao manipulam dados pessoais reais.

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

## Proibicoes

- Nao versionar backup.
- Nao colar credenciais no chat.
- Nao testar restore com dados reais nesta etapa.
