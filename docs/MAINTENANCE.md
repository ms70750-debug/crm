# Manutencao Yntelli - BBB Consig CRM

Este calendario vale para o MVP controlado e deve ser revisado antes de producao real.

## Toda segunda-feira - check-up semanal
- Confirmar `/healthz` do backend.
- Rodar testes essenciais e build.
- Revisar logs tecnicos sem expor CPF, telefone ou email completos.
- Verificar se `.env`, bancos locais, backups, `dist`, `node_modules`, `test-results` e `referencias/` continuam fora do Git.
- Confirmar que WhatsApp, INSS, FGTS e bancos seguem em modo simulacao.
- Conferir se existe backup local recente quando houver base de teste importante.

## Todo dia 1 - check-up mensal
- Rodar `npm audit --audit-level=moderate`.
- Revisar dependencias do backend e frontend.
- Revisar permissoes por perfil e usuarios demo.
- Revisar documentos de LGPD, ambiente e deploy.
- Conferir crescimento do banco SQLite e necessidade de PostgreSQL.
- Revisar performance basica de dashboard, leads, clientes e propostas.

## Trimestral - auditoria estrutural
- Revisar arquivos acima de 500 linhas.
- Revisar arquitetura, regras de negocio, data model e ADRs.
- Reavaliar necessidade de migracao para PostgreSQL.
- Reavaliar autenticacao, cookies seguros, criptografia em repouso, backup/restore e monitoramento.
- Gerar relatorio em `docs/audit/`.

## Bloqueio permanente
Este projeto ainda nao esta liberado para operacao real com dados pessoais de clientes. Uso atual permitido apenas para teste controlado com dados ficticios.
