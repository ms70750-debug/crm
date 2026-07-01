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

## Referencias analisadas
As referencias publicas foram baixadas em `referencias/` para inspiracao visual e conceitual. O sistema implementado e proprio, com dados ficticios e sem copia direta.

## Proximos passos recomendados
1. Adicionar autenticacao e perfis reais.
2. Criar testes automatizados de API e frontend.
3. Evoluir migrations com Alembic.
4. Conectar Evolution API em ambiente de homologacao.
5. Adicionar importacao de leads por CSV e funil kanban.
