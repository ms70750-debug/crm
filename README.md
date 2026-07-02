# BBB Consig CRM

CRM para operacao de credito consignado com leads, clientes, propostas, tarefas, consultas simuladas INSS/FGTS, WhatsApp simulado, treinamentos e administracao.

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
- CRUD em `/leads`, `/clientes`, `/propostas` e `/tarefas`
- `GET /consultas/inss/{cpf}`
- `GET /consultas/fgts/{cpf}`
- `POST /whatsapp/preview`
- `POST /whatsapp/simular-envio`

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

- Backend Render: veja `docs/DEPLOY-RENDER.md`.
- Frontend Vercel: veja `docs/DEPLOY-VERCEL.md`.
- Variaveis de ambiente: veja `docs/ENVIRONMENT.md`.
- Checklist pre-deploy: veja `docs/PRE-DEPLOY-CHECKLIST.md`.

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

## Banco de dados
O SQLite e criado automaticamente no startup do backend em `backend/app.db`. A migration inicial versionada esta em `backend/migrations/2026_06_30_initial_schema.sql`.

SQLite permanece como padrao local/controlado. Ele nao e recomendado para producao real com multiplos usuarios e dados sensiveis. O caminho futuro documentado e PostgreSQL via `DATABASE_URL`, com revisao de migrations e seguranca antes de publicar dados reais.

## Referencias analisadas
As referencias publicas foram baixadas em `referencias/` para inspiracao visual e conceitual. O sistema implementado e proprio, com dados ficticios e sem copia direta.

## Proximos passos recomendados
1. Homologar deploy controlado com dados ficticios.
2. Planejar migracao futura para PostgreSQL.
3. Evoluir migrations com Alembic.
4. Revisar seguranca/LGPD antes de dados reais.
5. Conectar integracoes externas somente em etapa futura aprovada.
