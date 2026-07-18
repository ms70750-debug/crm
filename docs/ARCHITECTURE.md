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
- PostgreSQL gerenciado fica preparado apenas por migrations e configuracao futura; nenhuma conexao real e necessaria no modo demo.

## Arquitetura Supabase BACKEND-ONLY
Para USO PROPRIO, o Supabase deve operar em arquitetura `BACKEND-ONLY`.

- O frontend nao deve usar `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY` ou cliente Supabase para CRUD direto.
- O frontend deve chamar somente a API FastAPI do backend.
- O backend deve acessar PostgreSQL por `DATABASE_URL` configurada apenas em ambiente seguro.
- `PUBLIC`, `anon` e `authenticated` nao devem ter acesso direto as tabelas do schema `public`.
- `service_role` nao pode ser exposto no frontend; se usado futuramente, deve ficar restrito a backend/ambiente seguro.
- RLS pode ser defesa adicional futura, mas nao substitui grants revogados quando o frontend nao acessa Supabase diretamente.

## Readiness para dados reais
O backend possui verificacao de prontidao para `APP_MODE=production`. Esse modo permanece bloqueado ate existirem `DATABASE_URL`, `BBB_DATA_ENCRYPTION_KEY`, `BBB_AUTH_SECRET` forte, migrations aplicadas, backup configurado, consentimento obrigatorio, logs mascarados, HTTPS esperado e testes criticos aprovados.

## Protecao de dados
Campos sensiveis devem usar envelope criptografado versionado com Fernet (`cryptography`) e hash deterministico separado para CPF. A chave `BBB_DATA_ENCRYPTION_KEY` deve existir somente em ambiente seguro e nunca no Git.

## Fluxo de dados
Frontend chama a API REST em `http://localhost:8000`. A API acessa SQLite via SQLAlchemy e devolve respostas JSON. Simulacoes e WhatsApp nao chamam servicos externos.

Em PostgreSQL/Supabase futuro, o fluxo permanece: frontend -> backend -> banco. A API publica do Supabase nao deve ser caminho de dados do CRM.

## Backup e restauracao

A fundacao de backup externo segue arquitetura operacional separada da aplicacao:

- O workflow ativo `Supabase Encrypted Backup` usa Supabase CLI oficial em GitHub Actions, nao o script legado direto de `pg_dump`.
- O Supabase CLI gera arquivos temporarios de roles, schema e dados; eles sao empacotados e criptografados antes do upload do artifact.
- O artifact publicado deve conter somente pacote `.tar.enc`, manifesto sanitizado e checksum externo.
- Arquivos SQL abertos existem apenas no runner temporario e nao devem ser enviados como artifact.
- Manifesto e checksums nao contem credenciais nem conteudo de cliente.
- O codigo legado de backup/preflight com SQLAlchemy normaliza URLs para `postgresql+psycopg://` e permanece coberto por testes, mas nao e o mecanismo ativo do workflow atual.
- Restore real continua proibido sem ambiente isolado e aprovacao explicita.
- Armazenamento externo real ainda nao esta ativado.

## Modo demo obrigatorio
O sistema deve permanecer com `APP_MODE=demo` nesta fase. Nesse modo:
- a interface exibe aviso visivel para nao inserir dados reais;
- cadastros e simulacoes bloqueiam CPF matematicamente valido;
- WhatsApp, INSS, FGTS, bancos e pagamentos permanecem simulados;
- usuarios demo existem apenas para validacao controlada do MVP.

Esse bloqueio e reversivel somente em etapa futura aprovada, com ADR, revisao LGPD e controles de producao real.

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
- Dados pessoais completos aparecem somente para admin, supervisor e operador; parceiro, logs e relatorios gerais devem permanecer mascarados/limitados.
- SQLite nao e adequado para producao real ou operacao SaaS multiusuario.
- Autenticacao atual e adequada apenas para MVP controlado.
- Integracoes externas devem ter timeout, retry, cache e auditoria antes de uso real.

## Headers e rate limit
O backend deve aplicar headers basicos de seguranca e limites em login/rotas sensiveis. Esses controles sao baseline demo e nao substituem WAF/proxy em producao.

## Sessao
A sessao atual usa cookie HttpOnly. Em producao controlada o cookie deve ser `Secure` e `SameSite=None` para permitir frontend e backend em provedores diferentes. Em local, usa `SameSite=Lax`. O token Bearer ainda e aceito pelo backend para testes e compatibilidade, mas o frontend nao persiste token em localStorage.

## Fail modes
- Banco local ausente: API recria estrutura basica.
- Migration incompleta: app pode falhar no startup.
- API fora do ar: frontend mostra erro de carregamento.
- Sem opt-in: WhatsApp simulado deve bloquear registro.

## Integracoes futuras
- Evolution API para WhatsApp real, somente apos opt-in, auditoria e homologacao.
- Bancos/INSS/FGTS reais somente apos validacao comercial, juridica e tecnica.

## Render e cold start
O health check publicado respondeu apos nova tentativa durante a auditoria. Esse comportamento e compatavel com cold start/latencia de servico gerenciado. Nao houve alteracao de plano ou infraestrutura nesta recuperacao.
