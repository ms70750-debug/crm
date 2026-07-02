# ADR 010 - Producao real exige PostgreSQL

## Status
Proposed

## Contexto
SQLite atende o MVP local/controlado, mas nao e adequado para operacao real com multiplos usuarios, concorrencia, backups formais e dados pessoais.

## Decisao proposta
Antes de qualquer producao real com dados de clientes, migrar para PostgreSQL gerenciado.

## Criterios de migracao
- Uso de dados reais.
- Mais de 10 usuarios internos.
- Operacao diaria continua.
- Necessidade de backup e restore formais.
- Integracao real com WhatsApp, INSS, FGTS ou bancos.
- Qualquer intencao de SaaS.

## Consequencias
- SQLite permanece somente para local/teste controlado.
- `DATABASE_URL` ja existe como caminho futuro.
- A migracao deve revisar tipos, indices, migrations, backup, restore, LGPD e performance.
