# BBB Consig CRM

CRM para operacao de credito consignado com leads, clientes, propostas, tarefas, consultas simuladas INSS/FGTS, WhatsApp simulado, treinamentos e administracao.

## Status do projeto
STATUS ATUAL: MVP CONTROLADO - USO SOMENTE COM DADOS FICTICIOS.

NAO AUTORIZADO PARA DADOS REAIS ATE APROVACAO FINAL.

Classificacao atual: **USO_PROPRIO - MVP CONTROLADO**.

Este projeto ainda nao esta liberado para operacao real com dados pessoais de clientes. Uso atual permitido apenas para teste controlado com dados ficticios.

- Publico esperado agora: dono da operacao e equipe interna restrita.
- Capacidade alvo do MVP: ate 10 usuarios internos.
- Dados permitidos: ficticios ou anonimizados.
- Dados proibidos nesta fase: CPF real, conta bancaria real, beneficio real, margem real e contrato real.
- Modo esperado: `APP_MODE=demo`.
- No modo demo, CPFs matematicamente validos sao bloqueados em cadastros e simulacoes para reduzir risco de uso indevido.
- Producao real fica condicionada aos ADRs de hardening, PostgreSQL, backup/restore, monitoramento, criptografia em repouso, autenticacao segura e auditoria final.
- A fundacao tecnica de readiness ja existe para revisao, mas nao ativa uso com dados reais, WhatsApp real ou publicacao sem aprovacao explicita.
- Em 2026-07-18, a preparacao expressa confirmou testes locais, build, E2E e backup criptografado existente por metadados, sem executar nova publicacao.

## Stack
- Frontend: React, TypeScript, Vite, React Router, Tailwind CSS, Lucide React, Recharts, React Hook Form e Zod.
- Backend: Python, FastAPI, SQLite, SQLAlchemy, Pydantic e Uvicorn.

## Como rodar o backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

URL: `http://localhost:8000`

Rotas principais:
- `GET /healthz`
- `GET /dashboard/resumo`
- `POST /auth/login`
- `POST /auth/demo-login`
- `POST /auth/logout`
- CRUD em `/leads`, `/clientes`, `/propostas` e `/tarefas`
- `GET /consultas/inss/{cpf}`
- `GET /consultas/fgts/{cpf}`
- `POST /whatsapp/preview`
- `POST /whatsapp/simular-envio`
- `GET /whatsapp/status`

## Como rodar o frontend
```bash
cd frontend
npm install
npm run dev
```

URL: `http://localhost:5173`

## Comandos de validacao
```bash
backend\.venv\Scripts\python.exe -m pytest backend\tests -q
cd frontend
npm audit --audit-level=moderate
npm run build
npm run e2e
```

## Deploy controlado
Esta versao esta preparada para deploy controlado/teste, sem dados reais e sem integracoes reais com WhatsApp, INSS, FGTS ou bancos.

Mesmo no deploy controlado, mantenha `APP_MODE=demo`, `REAL_DATA_MODE=false` e `EVOLUTION_API_MODE=simulation`.

O deploy controlado pode ser aprovado para homologacao com dados ficticios quando backend, build frontend, E2E, varredura de secrets, backup ficticio/restore ficticio e smoke test de `/healthz` estiverem aprovados. Isso nao libera dados reais.

## Ambiente controlado online
Ambiente publicado somente para homologacao com dados ficticios ou anonimizados:

- Frontend Vercel: `https://crm-sepia-beta.vercel.app`
- Backend Render: `https://crm-2340.onrender.com`
- Health check: `https://crm-2340.onrender.com/healthz`

O uso com dados reais continua proibido nesta fase.

- Backend Render: veja `docs/DEPLOY-RENDER.md`.
- Frontend Vercel: veja `docs/DEPLOY-VERCEL.md`.
- Variaveis de ambiente: veja `docs/ENVIRONMENT.md`.
- Checklist pre-deploy: veja `docs/PRE-DEPLOY-CHECKLIST.md`.
- Rotina de manutencao: veja `docs/MAINTENANCE.md`.

Comando de start do backend em provedor:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Build do frontend:
```bash
cd frontend
npm run build
```

## Modulos
- Dashboard com cards, grafico e proximos contatos.
- Leads com cadastro, busca, filtros e pipeline.
- Clientes com cadastro e dados de beneficio.
- Consulta INSS e FGTS simuladas.
- Propostas com vinculo a cliente, valores, banco, produto e status.
- Tarefas com prioridade, status e conclusao.
- WhatsApp Simulado com previa, modelos e historico interno.
- Treinamentos com aulas, checklist, prompts e base inicial.
- Administracao com usuarios ficticios e Evolution API em simulacao.
- Aviso visivel de ambiente de demonstracao para impedir uso de dados reais.

## Banco de dados
O SQLite e criado automaticamente no startup do backend em `backend/app.db`. A migration inicial versionada esta em `backend/migrations/2026_06_30_initial_schema.sql`.

SQLite permanece como padrao local/controlado. Ele nao e recomendado para producao real com multiplos usuarios e dados sensiveis. O caminho futuro documentado e PostgreSQL via `DATABASE_URL`, com revisao de migrations e seguranca antes de publicar dados reais.

## Referencias analisadas
As referencias publicas foram baixadas em `referencias/` para inspiracao visual e conceitual. O sistema implementado e proprio, com dados ficticios e sem copia direta.

## Proximos passos recomendados
1. Aprovar formalmente a publicacao controlada ou manter o ambiente atual sem mudancas.
2. Homologar somente com dados ficticios.
3. Planejar migracao futura para PostgreSQL.
4. Revisar seguranca/LGPD antes de dados reais.
5. Conectar integracoes externas somente em etapa futura aprovada.
