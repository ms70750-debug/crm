# ADR 010 - Producao real exige PostgreSQL

## Status
Accepted

## Contexto
SQLite atende o MVP local/controlado, mas nao e adequado para operacao real com multiplos usuarios, concorrencia, backups formais e dados pessoais.

## Decisao
Producao real com dados de clientes exige PostgreSQL gerenciado.

SQLite permanece permitido apenas para desenvolvimento, testes locais e MVP controlado com dados ficticios ou anonimizados.

Supabase PostgreSQL foi escolhido como provedor gerenciado inicial para preparacao futura. O runtime da API deve usar `DATABASE_URL` pelo pooler de transaction-mode. Migrations/admin devem usar `DIRECT_URL` pelo pooler de session-mode.

## Criterios de migracao
- Uso de dados reais.
- Mais de 10 usuarios internos.
- Operacao diaria continua.
- Necessidade de backup e restore formais.
- Integracao real com WhatsApp, INSS, FGTS ou bancos.
- Qualquer intencao de SaaS.

## Consequencias
- SQLite permanece somente para local/teste controlado.
- `DATABASE_URL` real deve existir apenas no painel seguro do provedor.
- `DIRECT_URL` real deve existir apenas no ambiente seguro usado para migrations/admin.
- A migracao deve revisar tipos, indices, migrations, backup, restore, LGPD e performance.
- Migrations PostgreSQL devem ficar separadas das migrations SQLite e usar SQL compativel com PostgreSQL.
- `Base.metadata.create_all` nao e estrategia final de producao real; e apenas bootstrap local/controlado.
- Supabase nao altera o bloqueio de dados reais; `REAL_DATA_MODE` permanece `false`.
- A proxima etapa obrigatoria depois de PostgreSQL e definir criptografia/protecao de dados pessoais em repouso.
- Uso com dados reais continua bloqueado ate concluir criptografia, autenticacao segura, backup/restore, monitoramento e revisao LGPD.
