# Implantacao Local

## Backend
1. Criar ambiente virtual em `backend/.venv`.
2. Instalar `backend/requirements.txt`.
3. Rodar `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` dentro de `backend`.

## Frontend
1. Instalar dependencias em `frontend`.
2. Rodar `npm run dev`.
3. Acessar `http://localhost:5173`.

## Banco
O SQLite e criado automaticamente em `backend/app.db` no startup. A migration de referencia fica em `backend/migrations/2026_06_30_initial_schema.sql`.
