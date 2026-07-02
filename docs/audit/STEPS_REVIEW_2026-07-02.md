# Relatório de Etapas Yntelli — BBB Consig CRM

## Resumo executivo
O BBB Consig CRM seguiu majoritariamente o padrão Yntelli para um MVP/controlado: há documentação de fundação, ADRs, migrations, testes, deploy controlado, login/perfis, audit log, opt-in e simulações com snapshot. O projeto está no GitHub e a branch `main` está sincronizada com `origin/main`.

Ainda existem pontos de atenção antes de produção real: não há rotina formal de manutenção semanal/mensal/trimestral, SQLite permanece apenas adequado para teste controlado, dados pessoais não estão criptografados em repouso e autenticação usa token local sem cookies HttpOnly/Secure. O projeto está apto para uso controlado com dados fictícios, mas não para operação real com dados de clientes sem a próxima rodada de hardening.

## Nota geral
8/10

## Status por etapa

| Etapa | Status | Observação |
|---|---|---|
| Descoberta | Atenção | README explica o produto e o MVP/controlado, mas não classifica explicitamente como USO_PRÓPRIO ou SAAS e não documenta número esperado de usuários. |
| Fundação | OK | Arquivos obrigatórios, docs, ADRs, audit, gitignore e env examples existem. |
| Construção | OK | Histórico em commits/branches, CHANGELOG, migrations, testes backend e E2E presentes. Regras demonstrativas centralizadas em `backend/app/config/business_rules/produtos.py`. |
| Publicação | OK | Deploy controlado documentado para Render/Vercel, `render.yaml`, `frontend/vercel.json`, build/audit/testes passando. Produção real ainda marcada como futura. |
| Manutenção | Atenção | Existe `docs/audit/`, mas não há rotina formal de check-up semanal, mensal e auditoria trimestral. |

## Pendências críticas
- Não usar dados reais ainda: SQLite é documentado como teste controlado e não é recomendado para produção real multiusuário.
- Dados pessoais não estão criptografados em repouso; há controle por perfil e mascaramento para parceiro/logs, mas não criptografia de banco/campos.
- Autenticação usa token no frontend/localStorage; cookies HttpOnly/Secure não se aplicam hoje e devem ser revistos para produção real.
- Não há monitoramento/backup/restore de produção documentado para operação real.

## Pendências importantes
- Explicitar no README ou `spec.md` se o produto é USO_PRÓPRIO ou SAAS.
- Documentar quantidade esperada de usuários e capacidade alvo.
- Atualizar `CHANGELOG.md` com as etapas mais recentes: login/perfis, visualização operacional e deploy controlado.
- Criar rotina de manutenção: check-up semanal, mensal e auditoria trimestral.
- Ajustar `docs/BUSINESS-RULES.md`: ele ainda fala que CPF deve ser mascarado por padrão, mas a regra atual permite dados completos para admin/supervisor/operador e mascara parceiro/logs.
- Adicionar alerta/runtime check para variáveis obrigatórias em deploy, especialmente `BBB_AUTH_SECRET` e `CORS_ORIGINS`.
- Avaliar mover autenticação para cookies seguros ou fortalecer proteção contra XSS antes de produção real.

## Melhorias futuras
- Migrar de SQLite para PostgreSQL gerenciado antes de dados reais.
- Adotar Alembic ou ferramenta formal de migrations.
- Criar `docs/MAINTENANCE.md` com rotinas semanais/mensais/trimestrais.
- Adicionar testes de autorização mais granulares por tela/perfil.
- Separar serviços externos futuros em módulos isolados com timeout, retry, cache e feature flag antes de qualquer integração real.
- Implementar criptografia de campos sensíveis ou estratégia equivalente de proteção em repouso.
- Revisar logs técnicos em ambiente hospedado para garantir ausência de CPF completo.

## Evidências por área

### Descoberta
- `README.md` informa que o projeto é um CRM para operação de crédito consignado com leads, clientes, propostas, tarefas, consultas simuladas INSS/FGTS e WhatsApp simulado.
- `README.md` e docs de deploy deixam claro que a versão atual é controlada/teste e sem dados reais.
- `docs/CAPACITY.md` diferencia MVP local/demo de cenário SaaS/multiusuário.
- Falta classificação textual explícita: `USO_PRÓPRIO` ou `SAAS`.
- Falta número esperado de usuários.

### Fundação
Arquivos encontrados:
- `README.md`
- `CHANGELOG.md`
- `AGENTS.md`
- `AGENTS-JUNIOR.md`
- `CLAUDE.md`
- `DO-NOT-TOUCH.md`
- `.gitignore`
- `.env.example`
- `docs/ARCHITECTURE.md`
- `docs/DATA-MODEL.md`
- `docs/BUSINESS-RULES.md`
- `docs/CAPACITY.md`
- `docs/DEPLOY.md`
- `docs/adr/`
- `docs/audit/`

GitHub:
- Remote: `https://github.com/ms70750-debug/crm.git`
- Branch atual: `main`
- Último commit: `5a7ecce chore: prepara projeto para deploy controlado`

### Decisões técnicas
ADRs encontrados:
- `001-banco-de-dados.md`
- `002-backend.md`
- `003-frontend.md`
- `004-autenticacao.md`
- `005-lgpd-dados-pessoais.md`
- `006-comunicacao-whatsapp.md`
- `007-regras-negocio.md`
- `008-deploy.md`

As decisões principais de banco, backend, frontend, autenticação, LGPD, WhatsApp, regras de negócio e deploy estão documentadas. Não identifiquei troca de stack sem ADR.

### Construção
- Histórico de commits mostra evolução por etapas: criação inicial, validação local, melhoria de leads, segurança/LGPD, login/perfis, visualização de dados sensíveis e deploy controlado.
- `CHANGELOG.md` registra fases iniciais, mas está desatualizado frente aos últimos commits.
- Testes principais existem:
  - Backend: `backend/tests/test_security_flows.py`
  - E2E: `frontend/e2e/auth-flow.spec.ts`, `frontend/e2e/security-flow.spec.ts`
- Arquivos acima de 500 linhas:
  - `frontend/package-lock.json` com mais de 500 linhas, esperado para lockfile.
  - Nenhum arquivo fonte relevante acima de 500 linhas foi identificado.
- Regras demonstrativas de produto estão em `backend/app/config/business_rules/produtos.py`.
- Ainda há valores demo em seeds e defaults de UI, aceitáveis para MVP, mas não substituem política comercial real.

### Banco e LGPD
- `docs/DATA-MODEL.md` contém ERD em Mermaid.
- Migrations encontradas:
  - `2026_06_30_initial_schema.sql`
  - `2026_07_01_fundacao_seguranca_lgpd.sql`
  - `2026_07_01_leads_etapa_2.sql`
  - `2026_07_01_auth_etapa_3.sql`
- Dados pessoais:
  - Admin/supervisor/operador veem dados completos para operação.
  - Parceiro recebe dados mascarados/limitados.
  - Audit logs sanitizam CPF, telefone e e-mail via `sanitize_metadata`.
- Soft delete:
  - `clientes.deleted_at` existe e rota de delete aplica soft delete.
- Audit log:
  - Login, cliente, consentimento, WhatsApp simulado e simulação INSS/FGTS registram auditoria.
- Pendência: sem criptografia de dados em repouso.

### Segurança
- `.env` está no `.gitignore`.
- `.env.example` existe e contém placeholders, sem segredos reais.
- Não encontrei chaves secretas reais no código; há senhas demo e placeholders documentados.
- Headers de segurança equivalentes a Helmet estão no middleware:
  - `X-Content-Type-Options`
  - `X-Frame-Options`
  - `Referrer-Policy`
  - `Permissions-Policy`
  - `Content-Security-Policy`
- Rate limit existe para login e rotas sensíveis.
- Cookies HttpOnly/Secure: não aplicável hoje, pois a sessão usa Bearer token/localStorage. Atenção para produção.
- Webhooks: não há webhooks reais implementados.

### Integrações
| Integração | Status | Pasta isolada | Timeout | Retry | Cache | Feature flag | Tratamento de erro |
|---|---|---:|---:|---:|---:|---:|---:|
| WhatsApp/Evolution API | Simulado | Parcial (`routes/whatsapp.py`) | N/A | N/A | N/A | Sim (`EVOLUTION_API_MODE=simulation`) | Sim, bloqueia sem opt-in |
| INSS | Simulado | Parcial (`services/simulations.py`) | N/A | N/A | N/A | Simulação por design | Sim |
| FGTS | Simulado | Parcial (`services/simulations.py`) | N/A | N/A | N/A | Simulação por design | Sim |
| Bancos/consignado | Simulado/dados fictícios | Não há integração real | N/A | N/A | N/A | Simulação por design | N/A |
| IA | Apenas prompts/documentos | `prompts/` | N/A | N/A | N/A | N/A | N/A |
| Pagamento | Não encontrado | N/A | N/A | N/A | N/A | N/A | N/A |
| Email | Não encontrado | N/A | N/A | N/A | N/A | N/A | N/A |
| Storage | Não encontrado | N/A | N/A | N/A | N/A | N/A | N/A |
| Deploy | Render/Vercel documentado | `render.yaml`, `frontend/vercel.json`, docs | N/A | N/A | N/A | Config por env | Healthcheck |

Como não há APIs externas reais, timeout/retry/cache não são exigíveis agora, mas estão documentados como requisito antes de integrar serviços reais.

### Publicação
- `docs/DEPLOY.md`, `docs/DEPLOY-RENDER.md`, `docs/DEPLOY-VERCEL.md`, `docs/ENVIRONMENT.md` e `docs/PRE-DEPLOY-CHECKLIST.md` existem.
- `render.yaml` existe para backend.
- `frontend/vercel.json` existe para SPA fallback.
- `npm run build` passou.
- `npm audit --audit-level=moderate` passou com 0 vulnerabilidades.
- Testes backend e E2E passaram.
- Produção real não está documentada como ativa; o projeto está preparado para deploy controlado/teste.
- Alerta de variáveis existe em docs, mas não há verificação automática de env vars faltantes.

### Manutenção
- Existe relatório anterior em `docs/audit/INVESTIGATION_2026-07-01.md`.
- Este relatório passa a registrar revisão de etapas em `docs/audit/STEPS_REVIEW_2026-07-02.md`.
- Não encontrei rotina formal de check-up semanal, check-up mensal ou auditoria trimestral.

## Validação executada
- `backend\.venv\Scripts\python.exe -m pytest backend\tests -q`
  - Resultado: `5 passed`
- `npm audit --audit-level=moderate`
  - Resultado: `found 0 vulnerabilities`
- `npm run build`
  - Resultado: passou, com aviso de chunk Vite acima de 500 kB.
- `npm run e2e`
  - Resultado: `2 passed`

## Os 12 Pecados Yntelli

| Pecado | Encontrado? | Evidência | Gravidade |
|---|---|---|---|
| 1. Regra de negócio em texto solto | Parcial | Regras demonstrativas centralizadas em config, mas docs e UI ainda têm alguns defaults demo. | Média |
| 2. IA trocando stack sem ADR | Não | ADRs cobrem backend, frontend, banco, auth e deploy. | Baixa |
| 3. Resquícios de projeto copiado | Não | README informa referências apenas como inspiração e `referencias/` está fora do Git. | Baixa |
| 4. Monolito embolado | Não crítico | Estrutura simples e separada por routes/services/models/pages; adequada ao MVP. | Baixa |
| 5. Migrations sem ERD | Não | `docs/DATA-MODEL.md` contém ERD e migrations existem. | Baixa |
| 6. Operação lenta travando requisição | Não observado | Simulações são locais e simples; sem integrações lentas reais. | Baixa |
| 7. Ignorar AGENTS.md | Não observado | `AGENTS.md` e arquivos auxiliares existem. | Baixa |
| 8. Dados pessoais sem criptografia | Sim | Há autorização/mascaramento/audit, mas sem criptografia em repouso. | Alta para produção real |
| 9. API externa sem cache e retry | Não aplicável agora | Não há API externa real; requisito documentado para futuro. | Baixa |
| 10. Margem/regra de convênio hardcoded | Parcial | Regras demo estão centralizadas em config, mas ainda são fictícias e não comerciais. | Média |
| 11. Comunicação sem opt-in registrado | Não | WhatsApp simulado exige consentimento ativo. | Baixa |
| 12. Simulação sem snapshot de auditoria | Não | Simulações INSS/FGTS geram snapshot/hash e audit log. | Baixa |

## Veredito final
A) Projeto seguiu o padrão Yntelli

Com ressalva: está aprovado para continuidade e deploy controlado com dados fictícios. Para produção real com dados de clientes, precisa resolver as pendências críticas de PostgreSQL, criptografia/segurança em repouso, rotina de manutenção e hardening de autenticação.
