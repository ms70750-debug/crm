# Capacidade

## Capacidade atual
Ambiente local/demo para validacao de fluxo e treinamento.

## SQLite
SQLite e suficiente para MVP local, testes e demonstracao. Nao e recomendado para SaaS multiusuario, alta concorrencia ou auditoria regulatoria robusta.

## Limite recomendado
Migrar para PostgreSQL antes de:
- usuarios simultaneos reais;
- dados reais de clientes;
- integracoes externas;
- deploy publico;
- necessidade de backups/restore auditaveis.

## Alertas SaaS
Antes de SaaS, implementar autenticacao completa, isolamento por tenant, criptografia/mascaramento, logs seguros, backups, monitoramento e politicas LGPD.
