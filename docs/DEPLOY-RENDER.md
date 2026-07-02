# Deploy Controlado do Backend no Render

Este guia prepara um ambiente de teste controlado para a API FastAPI do BBB Consig CRM.

## Escopo
- Backend: `backend/app/main.py`
- Healthcheck: `/healthz`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- WhatsApp, INSS, FGTS e bancos externos continuam em modo simulacao.

## Blueprint
O arquivo `render.yaml` fica na raiz do repositorio, como esperado pelo Render Blueprint. Ele define um Web Service Python com `rootDir: backend`, `buildCommand` e `startCommand`.

## Variaveis obrigatorias
- `BBB_AUTH_SECRET`: segredo forte criado no painel do Render.
- `CORS_ORIGINS`: dominio publico do frontend Vercel, exemplo `https://seu-app.vercel.app`.
- `DATABASE_URL`: manter `sqlite:///./app.db` apenas em teste controlado.
- `EVOLUTION_API_MODE`: manter `simulation`.

## SQLite agora, PostgreSQL depois
SQLite e aceitavel somente para validacao local/controlada. Nao e recomendado para producao real com multiplos usuarios, concorrencia e dados sensiveis. O caminho futuro sera PostgreSQL gerenciado, com `DATABASE_URL` apontando para o banco e migration revisada antes da publicacao real.

## Checklist rapido
1. Confirmar que `.env`, `app.db`, backups e logs nao estao no Git.
2. Criar `BBB_AUTH_SECRET` no painel do Render.
3. Configurar `CORS_ORIGINS` com o dominio real da Vercel.
4. Fazer deploy do backend.
5. Abrir `https://SEU-BACKEND.onrender.com/healthz`.
6. Testar login com usuarios demo apenas em base ficticia.

## Cuidados LGPD
CPF, telefone, e-mail, beneficio e observacoes operacionais exigem ambiente seguro. Nao publique dados reais enquanto HTTPS, variaveis, acesso, backup, retencao de logs e banco definitivo nao estiverem validados.
