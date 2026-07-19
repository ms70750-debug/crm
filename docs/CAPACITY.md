# Capacidade

## Capacidade atual
Ambiente local/demo e deploy controlado para validacao de fluxo, treinamento e homologacao com dados ficticios.

- Classificacao: USO_PROPRIO - MVP CONTROLADO.
- Publico esperado: dono da operacao e equipe interna restrita.
- Capacidade alvo do MVP: ate 10 usuarios internos.
- Dados permitidos: ficticios ou anonimizados.
- Dados reais de clientes permanecem proibidos nesta fase.

## SQLite
SQLite e suficiente para MVP local, testes, demonstracao e deploy controlado com baixo volume. Ele nao e recomendado para producao real, multiplos usuarios simultaneos, operacao diaria continua com dados pessoais ou auditoria regulatoria robusta.

## Limite recomendado
Migrar para PostgreSQL antes de:
- usar dados reais de clientes;
- passar de 10 usuarios internos;
- operar diariamente de forma continua;
- exigir backup e restore formais;
- integrar WhatsApp, INSS, FGTS ou bancos reais;
- publicar como SaaS ou atender terceiros;
- precisar de controle robusto de concorrencia, auditoria e performance.

## Gatilhos objetivos para migracao
- Qualquer CPF, beneficio, conta, agencia, endereco ou contrato real.
- Qualquer intencao de virar SaaS.
- Crescimento acima de 10 usuarios internos.
- Necessidade de restore testado e politicas formais de backup.
- Rotina comercial diaria dependente do sistema online.

## Capacidade alvo para uso proprio real
Para piloto interno com dados reais, preparar PostgreSQL gerenciado, pool de conexoes, backup diario criptografado, restore testado e monitoramento basico. O alvo inicial continua equipe interna restrita; se houver expansao para terceiros, tratar como SaaS e bloquear ate ADR de multi-tenancy.

## Alertas SaaS
Antes de SaaS, implementar autenticacao completa, isolamento por tenant, criptografia/mascaramento, logs seguros, backups, monitoramento e politicas LGPD.
