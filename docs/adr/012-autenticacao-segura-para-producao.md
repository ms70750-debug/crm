# ADR 012 - Autenticacao segura para producao

## Status
Proposed

## Contexto
A autenticacao atual usa token Bearer no frontend e localStorage, adequada apenas para MVP controlado com usuarios ficticios.

## Decisao proposta
Para producao real, substituir ou complementar a sessao atual por cookies HttpOnly, Secure e SameSite, com politica de expiracao, refresh, protecao contra XSS/CSRF conforme desenho final e revisao de autorizacao por perfil.

## Consequencias
- localStorage continua aceito apenas no MVP controlado.
- Producao real exige revisao de sessao, logout, expiracao, auditoria de login e possivel MFA.
- Nenhuma mudanca de auth sera feita sem ADR aprovado e testes de regressao.
