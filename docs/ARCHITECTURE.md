# Arquitetura - BBB Consig CRM

## Visao geral
BBB Consig CRM e um CRM local/demo para operacao de credito consignado. Ele organiza leads, clientes, propostas, tarefas, consultas simuladas, WhatsApp simulado, treinamentos e administracao.

## Frontend
- React com TypeScript e Vite.
- React Router para navegacao.
- Tailwind CSS para layout escuro com detalhes verde/lima.
- Recharts para graficos do dashboard.

## Backend
- FastAPI em Python.
- SQLAlchemy para acesso ao SQLite.
- Pydantic para schemas.
- Uvicorn para execucao local.

## Banco
- SQLite local em `backend/app.db`.
- Migrations versionadas em `backend/migrations`.
- Dados atuais sao ficticios.

## Fluxo de dados
Frontend chama a API REST em `http://localhost:8000`. A API acessa SQLite via SQLAlchemy e devolve respostas JSON. Simulacoes e WhatsApp nao chamam servicos externos.

## Telas principais
- Dashboard
- Leads
- Detalhe do lead
- Clientes
- INSS/FGTS simulados
- Propostas
- Tarefas
- WhatsApp Simulado
- Treinamentos
- Administracao

## Rotas principais
- `GET /healthz`
- `GET /dashboard/resumo`
- CRUD em `/leads`, `/clientes`, `/propostas`, `/tarefas`
- `GET /consultas/inss/{cpf}`
- `GET /consultas/fgts/{cpf}`
- `POST /whatsapp/preview`
- `POST /whatsapp/simular-envio`

## Pontos de risco
- Dados pessoais precisam ser mascarados e auditados.
- SQLite nao e adequado para operacao SaaS multiusuario.
- Autenticacao atual e minima/demo.
- Integracoes externas devem ter timeout, retry, cache e auditoria antes de uso real.

## Headers e rate limit
O backend deve aplicar headers basicos de seguranca e limites em login/rotas sensiveis. Esses controles sao baseline demo e nao substituem WAF/proxy em producao.

## Fail modes
- Banco local ausente: API recria estrutura basica.
- Migration incompleta: app pode falhar no startup.
- API fora do ar: frontend mostra erro de carregamento.
- Sem opt-in: WhatsApp simulado deve bloquear registro.

## Integracoes futuras
- Evolution API para WhatsApp real, somente apos opt-in, auditoria e homologacao.
- Bancos/INSS/FGTS reais somente apos validacao comercial, juridica e tecnica.
