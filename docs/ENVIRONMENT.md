# Variaveis de Ambiente

Nunca versionar `.env` real. Use `.env.example` e configure valores no painel do provedor.

## Backend

| Variavel | Exemplo local | Obrigatoria | Observacao |
|---|---|---|---|
| `APP_ENV` | `local` | Sim em deploy | Use `production` no Render para ativar validacao de ambiente. |
| `BACKEND_HOST` | `0.0.0.0` | Local | Usada nos comandos locais. |
| `BACKEND_PORT` | `8000` | Local | Render fornece `$PORT`. |
| `BBB_AUTH_SECRET` | `troque-este-valor` | Sim | Deve ser forte e secreto em deploy. |
| `CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Sim | Em deploy, usar somente dominios permitidos. |
| `DATABASE_URL` | `sqlite:///./app.db` | Sim | SQLite local/controlado agora; PostgreSQL futuro. |
| `EVOLUTION_API_MODE` | `simulation` | Sim | Manter `simulation` nesta fase. |
| `EVOLUTION_API_URL` | vazio | Nao | Nao configurar envio real agora. |
| `EVOLUTION_API_TOKEN` | vazio | Nao | Nunca commitar tokens. |

## Frontend

| Variavel | Exemplo local | Obrigatoria | Observacao |
|---|---|---|---|
| `VITE_API_URL` | `http://localhost:8000` | Sim | Em Vercel, usar URL publica do backend. |

## PostgreSQL Futuro

O projeto aceita `DATABASE_URL`, mas a base oficial continua SQLite local nesta etapa. Antes de migrar para PostgreSQL, revisar tipos, migrations, backups, concorrencia, retencao de dados e politicas LGPD.

## Dados Sensiveis

CPF, telefone, e-mail, beneficio, matricula e observacoes operacionais podem aparecer para perfis autorizados. Use apenas ambiente seguro e dados ficticios enquanto a operacao online nao estiver homologada.

## Validacao em runtime

Quando `APP_ENV=production`, o backend valida variaveis obrigatorias no startup e registra erro claro sem imprimir valores sensiveis. A aplicacao nao deve iniciar se:
- `BBB_AUTH_SECRET` estiver ausente ou com valor demo/placeholder.
- `CORS_ORIGINS` estiver ausente ou com placeholder.
- `DATABASE_URL` estiver ausente.
- `EVOLUTION_API_MODE` nao estiver como `simulation`.
