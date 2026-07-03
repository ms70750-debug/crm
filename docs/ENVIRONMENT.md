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
| `DATABASE_URL` | vazio no exemplo | Sim em deploy | Runtime da API. Em Supabase, usar a URL do pooler transaction-mode. SQLite local e MVP controlado continuam permitidos. |
| `DIRECT_URL` | vazio no exemplo | Nao para runtime | Uso exclusivo de migrations/admin. Em Supabase, usar a URL do pooler session-mode. |
| `REAL_DATA_MODE` | `false` | Sim em deploy | Manter `false` ate concluir PostgreSQL, criptografia, autenticacao segura, backup/restore, monitoramento e revisao LGPD. |
| `EVOLUTION_API_MODE` | `simulation` | Sim | Manter `simulation` nesta fase. |
| `EVOLUTION_API_URL` | vazio | Nao | Nao configurar envio real agora. |
| `EVOLUTION_API_TOKEN` | vazio | Nao | Nunca commitar tokens. |

## Frontend

| Variavel | Exemplo local | Obrigatoria | Observacao |
|---|---|---|---|
| `VITE_API_URL` | `http://localhost:8000` | Sim | Em Vercel, usar URL publica do backend. |

## PostgreSQL

O projeto aceita `DATABASE_URL`. Para desenvolvimento e MVP controlado, SQLite continua permitido. Para producao real com dados de clientes, `DATABASE_URL` deve apontar para PostgreSQL gerenciado e ficar somente no painel seguro do provedor.

Nunca commitar `.env` e nunca colar a `DATABASE_URL` real no chat.

Para Supabase:
- `DATABASE_URL`: usar no runtime da API, normalmente a conexao do shared transaction-mode pooler.
- `DIRECT_URL`: usar apenas para migrations/admin, normalmente a conexao do shared session-mode pooler.
- Substituir `[YOUR-PASSWORD]` somente no painel seguro do provedor ou variavel de ambiente local privada.
- Nunca colar senha, `DATABASE_URL` ou `DIRECT_URL` reais no chat.

`DATABASE_URL` define qual estrategia de banco sera usada:
- `sqlite:///...`: desenvolvimento, testes locais e MVP controlado.
- `postgresql://...`, `postgres://...` ou `postgresql+psycopg://...`: PostgreSQL gerenciado futuro.

Mesmo com PostgreSQL configurado, `REAL_DATA_MODE=true` continua bloqueado ate concluir criptografia, autenticacao segura, backup/restore, monitoramento e revisao LGPD.

`DIRECT_URL` nao e obrigatoria para o runtime da API. Ela e exigida apenas pelo script manual de migrations PostgreSQL.

Para dry-run via GitHub Actions, configurar o Repository Secret `SUPABASE_DIRECT_URL`. O workflow manual exporta esse secret como `DIRECT_URL` somente durante a execucao do dry-run e nao deve imprimir usuario, host, senha ou URL completa. Os logs devem mostrar apenas que a `DIRECT_URL` foi configurada e ocultada.

Se o dry-run reportar `DIRECT_URL invalida` ou `Invalid IPv6 URL`, confira o secret `SUPABASE_DIRECT_URL`: geralmente `[YOUR-PASSWORD]` nao foi substituido ou a senha contem caracteres reservados. Nunca cole a URL no chat; prefira senha forte com letras e numeros sem caracteres reservados ou use URL encoding.

## Dados Sensiveis

CPF, telefone, e-mail, beneficio, matricula e observacoes operacionais podem aparecer para perfis autorizados. Use apenas ambiente seguro e dados ficticios enquanto a operacao online nao estiver homologada.

## Validacao em runtime

Quando `APP_ENV=production`, o backend valida variaveis obrigatorias no startup e registra erro claro sem imprimir valores sensiveis. A aplicacao nao deve iniciar se:
- `BBB_AUTH_SECRET` estiver ausente ou com valor demo/placeholder.
- `CORS_ORIGINS` estiver ausente ou com placeholder.
- `DATABASE_URL` estiver ausente.
- `EVOLUTION_API_MODE` nao estiver como `simulation`.
- `REAL_DATA_MODE=true` estiver ativo sem PostgreSQL ou antes dos controles futuros obrigatorios.
