# ADR 013 - Backup, restore e monitoramento

## Status
Proposed

## Contexto
O deploy controlado atual nao deve ser confundido com producao real. Operacao com dados pessoais exige capacidade de recuperar dados e detectar falhas.

## Decisao proposta
Antes de producao real, definir e testar:
- Backup automatico.
- Restore validado.
- Retencao de logs.
- Monitoramento de disponibilidade.
- Alertas de erro.
- Processo de resposta a incidente.

## Consequencias
- Sem backup/restore testado, nao usar dados reais.
- Sem monitoramento, nao depender do sistema para operacao comercial continua.
- O checklist pre-deploy deve bloquear publicacao real enquanto estes itens estiverem pendentes.
