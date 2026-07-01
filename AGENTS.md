# BBB Consig CRM - Regras do Projeto

## Objetivo
Criar e manter o BBB Consig CRM, um sistema SaaS profissional para operacao de credito consignado com leads, clientes, propostas, tarefas, consultas simuladas, WhatsApp simulado, treinamentos e administracao.

## Mesa
Operacao de consignado com foco em INSS e FGTS.

## Stack obrigatoria
- Frontend: React, TypeScript, Vite, React Router, Tailwind CSS, Lucide React, Recharts, React Hook Form e Zod.
- Backend: Python, FastAPI, SQLite, SQLAlchemy, Pydantic e Uvicorn.

## Regras de produto
- Usar somente dados ficticios nesta primeira versao.
- Nao integrar bancos reais.
- Nao disparar WhatsApp real.
- Deixar a Evolution API preparada apenas em modo simulacao.
- Interface escura, moderna, profissional, com detalhes verde/lima.

## Regras tecnicas
- Toda mudanca estrutural de banco deve ter migration versionada em `backend/migrations`.
- Nunca gravar chaves reais no repositorio.
- Priorizar fluxos simples, testaveis e bem documentados.
- Manter backend e frontend separados em `backend/` e `frontend/`.
