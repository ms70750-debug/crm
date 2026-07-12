# Plano de Recuperacao Segura - 2026-07-12

Base exclusiva: `docs/audit/INVESTIGATION_FUNCTIONAL_2026-07-12.md`.

Hash inicial: `59fafcf3b29d6689974d5eb7a6d0d172cda710be`
Branch paralela: `fix/seguranca-pos-auditoria-2026-07-12`
Referencia local: `pre-security-recovery-2026-07-12`

## Baseline Antes das Correcoes

| Item | Resultado |
| --- | --- |
| Backend tests | `32 passed` |
| Frontend build | OK, com alerta de bundle JS > 500 kB |
| Frontend E2E | `2 passed` |
| Banco | SQLite local com tabelas `users`, `leads`, `clientes`, `propostas`, `tarefas`, `whatsapp_messages`, `audit_logs`, `consents`, `simulations`, `schema_migrations` |
| Variaveis `.env.example` | `APP_ENV`, `BACKEND_HOST`, `BACKEND_PORT`, `BBB_AUTH_SECRET`, `CORS_ORIGINS`, `DATABASE_URL`, `DIRECT_URL`, `REAL_DATA_MODE`, `VITE_API_URL`, `EVOLUTION_API_MODE`, `EVOLUTION_API_URL`, `EVOLUTION_API_TOKEN` |

## Matriz De Recuperacao

| ID | Problema | Evidencia da auditoria | Gravidade | Correcao proposta | Arquivos afetados | Teste de validacao |
| -- | -------- | ---------------------- | --------- | ----------------- | ----------------- | ------------------ |
| REC-001 | Escopo demo nao esta codificado como modo explicito | Critico: manter bloqueio de dados reais; `APP_MODE=demo` solicitado na recuperacao | Critica | Adicionar `APP_MODE=demo`, helpers de ambiente e aviso visivel no frontend | `.env.example`, `frontend/.env.example`, `backend/app/config/environment.py`, `frontend/src/components/Layout.tsx`, docs | Pytest bloqueando CPF valido no modo demo; E2E verifica aviso |
| REC-002 | Cadastro/consulta nao bloqueia CPF real no modo demo | Critico: projeto nao autorizado a dados pessoais reais | Critica | Bloquear CPF com checksum valido apenas em modo demo, sem impedir futura operacao aprovada | schemas de lead/cliente, rotas de simulacao, novo servico LGPD | Pytest com CPF valido rejeitado e CPF ficticio aceito |
| REC-003 | Sessao usa Bearer/localStorage e nao cookie HttpOnly | Critico: sessao via localStorage, sem cookie seguro | Critica | Adicionar cookie HttpOnly/SameSite, Secure em producao, `POST /auth/logout`, aceitar cookie no backend e parar de persistir token no localStorage | `backend/app/routes/auth.py`, `backend/app/services/security.py`, `frontend/src/lib/api.ts`, `frontend/src/auth/AuthContext.tsx`, testes | Pytest de cookie/logout; E2E login/logout existente |
| REC-004 | Demo users/senhas aparecem na tela de login | Critico: usuarios/senhas demo visiveis | Critica | Trocar botoes com senha visivel por login demo por perfil, permitido somente em `APP_MODE=demo` | `backend/app/routes/auth.py`, `frontend/src/pages/Login.tsx`, testes | Pytest bloqueia demo-login fora do modo demo; E2E usa demo-login |
| REC-005 | Criptografia em repouso ausente | Critico LGPD: sem criptografia em repouso | Critica | BLOQUEADO POR ADR: documentar decisao necessaria; nao improvisar chave/rotacao nesta tarefa | `docs/DATA-MODEL.md`, `docs/audit/RECOVERY_RESULT_2026-07-12.md` | Validacao documental |
| REC-006 | Multi-tenant/SaaS nao existe | Critico: nao pode ser SaaS real | Critica | BLOQUEADO POR DECISAO COMERCIAL E ADR: manter classificacao uso proprio MVP controlado | README/docs | Validacao documental |
| REC-007 | UI nao expoe status/exclusao para leads, propostas e tarefas | Importante: CRUDs parciais no frontend | Importante | Adicionar acoes simples e seguras ja suportadas pelo backend: status e exclusao conforme permissao | paginas Leads, Proposals, Tasks | E2E ou teste manual local, build |
| REC-008 | Revogacao de consentimento sem UI | Importante: rota existe, tela nao | Importante | Adicionar opt-out de WhatsApp na tela de clientes, sem envio real | `frontend/src/pages/Clients.tsx`, tipos | E2E de opt-in/opt-out ou teste backend |
| REC-009 | Auditoria incompleta para logout/status/propostas/tarefas/acesso negado | Etapa auditoria de acoes e itens importantes | Importante | Registrar logout, mudancas de status, criacao/alteracao/exclusao de propostas/tarefas/leads e tentativas negadas sem dados sensiveis | rotas backend e security service | Pytest verifica logs mascarados |
| REC-010 | Integracoes futuras sem modulo de health/simulacao documentado | Risco Yntelli 9; Evolution simulada sem health check externo | Importante | Manter sem chamada real, criar health/status simulado documentado | rota/admin/docs | Pytest/API status se aplicavel |
| REC-011 | Cobertura E2E insuficiente | Importante: poucas telas e fluxos | Importante | Ampliar E2E para aviso demo, consultas, lead detail, tarefas/propostas e admin conforme escopo | `frontend/e2e/*.spec.ts` | `npm run e2e` |
| REC-012 | 404 de recurso no login | Baixa: nao bloqueia fluxo | Melhoria | Adicionar favicon/manifest minimo ou validar ausencia de erro depois de build | `frontend/index.html` ou asset minimo | Playwright sem console 404 |
| REC-013 | Bundle >500 kB | Melhoria | Melhoria | BLOQUEADO/ADIADO: code splitting fora do escopo de recuperacao segura | resultado final | Build continua OK; pendencia registrada |
| REC-014 | FastAPI `on_event` e UTC naive | Melhoria | Melhoria | Adiar se nao necessario para criticos/importantes; registrar pendencia | resultado final | N/A |

## Decisoes De Escopo

* Nao migrar banco para PostgreSQL nesta tarefa.
* Nao implementar criptografia em repouso sem ADR de chave, rotacao e operacao.
* Nao transformar em SaaS.
* Nao publicar Render/Vercel.
* Nao usar dados reais.
* Preservar funcionalidades que ja passaram nos testes.
