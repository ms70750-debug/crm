# AUDITORIA FUNCIONAL YNTELLI

Data da auditoria: 2026-07-12
Projeto auditado: BBB Consig CRM
Modo: investigacao, sem correcao de codigo, sem commit, sem publicacao.

## 1. Resumo executivo

O projeto ja entrega um MVP controlado de CRM para consignado com login demo, dashboard, leads, clientes, propostas, tarefas, consultas INSS/FGTS simuladas, WhatsApp simulado com opt-in, treinamentos estaticos e administracao basica.

O que realmente funciona foi comprovado por build, API local, testes backend, testes E2E e navegacao local: login/logout, protecao de rotas, dashboard, criacao/listagem de cliente, opt-in, WhatsApp simulado, simulacoes INSS/FGTS com snapshot, permissoes de parceiro, soft delete de cliente, build frontend e deploy controlado respondendo.

Funciona parcialmente: CRUDs existem no backend, mas o frontend nao expoe todos os comandos de editar/excluir/status; Administracao lista usuarios e mostra configuracao, mas nao gerencia usuarios; Treinamentos e Evolution API sao telas informativas/estaticas; producao publicada esta online, mas continua controlada, com SQLite e sem validacao de logs/variaveis do provedor.

Quebrado: nao encontrei fluxo principal quebrado em execucao. Houve apenas um 404 de recurso na tela de login durante varredura Playwright, sem quebrar a aplicacao.

Ainda nao existe: recuperacao de senha, MFA, cookies HttpOnly/Secure, multi-tenant SaaS, upload de documentos, relatorios/exportacao, pagamentos, integracoes reais INSS/FGTS/bancos/WhatsApp, criacao/edicao de usuarios no painel, auditoria completa de producao e criptografia em repouso.

Principal risco atual: o sistema e funcional como MVP controlado com dados ficticios, mas nao esta pronto para operacao real/SaaS com dados pessoais porque usa SQLite no deploy controlado, token Bearer em localStorage, senha/usuarios demo visiveis, sem criptografia em repouso e sem multi-tenant.

## 2. Status geral

* Build: OK. `npm run build` passou; alerta de bundle JS com 745.49 kB.
* Execucao local: OK. Backend `/healthz` 200; frontend `/login` 200.
* Testes: 34 aprovados, 0 reprovados. Backend: 32 passed. Frontend E2E: 2 passed.
* Versao publicada: OK/PARCIAL. Backend Render respondeu 200 no segundo teste apos timeout inicial; frontend Vercel `/login` 200; login demo publicado chegou em `/dashboard`.
* Banco: OK para MVP controlado; PARCIAL para producao real.
* Seguranca: ATENCAO.
* Nota geral: 7.2 de 10 para MVP controlado; nao aprovado para dados reais.

## 3. Matriz funcional

| Funcionalidade | Tela | Backend | Banco | Teste executado | Status | Evidencia |
|---|---|---|---|---|---|---|
| Login demo | `/login` | `POST /auth/login`, `GET /auth/me` | `users`, `audit_logs` | Pytest, E2E, Playwright local/prod | FUNCIONA | `32 passed`; E2E auth passou; prod finalizou em `/dashboard` |
| Logout/protecao de rota | Layout/ProtectedRoute | `current_user` | `users` | E2E | FUNCIONA | `auth-flow.spec.ts` passou |
| Dashboard | `/dashboard` | `GET /dashboard/resumo` | leads, clientes, propostas, tarefas | API 200, pagina desktop/mobile | FUNCIONA | endpoint 200, rota abriu sem erro novo |
| Leads lista/criacao/filtros | `/leads` | CRUD `/leads` | `leads` | API 200, pagina abriu; backend coberto em permissoes | FUNCIONA PARCIALMENTE | criar/listar existe; editar/excluir/status nao expostos na tela |
| Detalhe do lead | `/leads/:id` | detalhe, timeline, historico, converter, gerar proposta | leads, clientes, propostas, tarefas, whatsapp | pagina abriu; backend lido | PRONTO, MAS NAO VALIDADO | rotas existem, mas E2E nao cobre converter/gerar proposta |
| Clientes | `/clientes` | CRUD `/clientes`, `/consents` | `clientes`, `consents`, `audit_logs` | Pytest, E2E, API 200 | FUNCIONA | cliente, opt-in e soft delete passaram |
| Propostas | `/propostas` | CRUD `/propostas` | `propostas` | API 200, pagina abriu | FUNCIONA PARCIALMENTE | criar/listar na tela; editar/excluir/status so backend |
| Tarefas | `/tarefas` | CRUD `/tarefas`, concluir | `tarefas` | API 200, pagina abriu | FUNCIONA PARCIALMENTE | criar/listar/concluir na tela; editar/excluir so backend |
| Consulta INSS | `/consulta-inss` | `GET /consultas/inss/{cpf}` | `simulations`, `audit_logs` | Pytest, API 200, pagina abriu | FUNCIONA | snapshot e regra_aplicada testados |
| Consulta FGTS | `/consulta-fgts` | `GET /consultas/fgts/{cpf}` | `simulations`, `audit_logs` | API 200, pagina abriu | FUNCIONA | endpoint 200 e persistencia de simulacao |
| WhatsApp simulado | `/whatsapp` | preview, simular-envio, historico | `whatsapp_messages`, `consents`, `audit_logs` | Pytest, E2E, API 200 | FUNCIONA | bloqueia sem opt-in e registra com opt-in |
| Treinamentos | `/treinamentos` | N/A | N/A | pagina abriu | INCOMPLETO | conteudo estatico em arrays locais |
| Administracao | `/admin` | `GET /auth/users` | `users` | API/pagina 200 | FUNCIONA PARCIALMENTE | lista usuarios; nao cria/edita/desativa |
| Deploy controlado | URLs README | Render/Vercel | SQLite Render declarado | HTTP direto e login demo | FUNCIONA PARCIALMENTE | health 200 apos retry; Vercel 200; sem logs/vars do provedor |

## 4. O que realmente funciona

* Build frontend com TypeScript e Vite.
* Instalacao frontend via `npm ci` e backend via `pip install -r requirements.txt`.
* Testes backend: 32 aprovados.
* Testes E2E: 2 aprovados.
* Login, logout, sessao via token, rota protegida e perfis.
* Cliente ficticio, opt-in WhatsApp, WhatsApp simulado, simulacao INSS e soft delete.
* Dashboard e endpoints principais respondem localmente.
* Todas as rotas principais abriram em desktop e mobile.
* Frontend publicado em Vercel responde e login demo entra no dashboard.
* Backend publicado em Render responde `/healthz` com `{"status":"ok","service":"BBB Consig CRM API"}`.

## 5. O que funciona parcialmente

* Leads: criar/listar/filtrar/detalhar existem; tela nao oferece edicao, exclusao ou mudanca direta de status.
* Propostas: criar/listar existem; backend tem editar/status/excluir, mas tela nao expoe esses comandos.
* Tarefas: criar/listar/concluir existem; backend tem editar/excluir, mas tela nao expoe.
* Administracao: lista usuarios demo e mostra Evolution API simulada; nao ha gestao real de usuarios/configuracoes.
* Deploy: online e validado por smoke test, mas ainda e ambiente controlado com SQLite e sem inspecao de logs/envs do provedor.

## 6. O que esta pronto, mas nao foi validado

* Conversao de lead em cliente e geracao de proposta pelo detalhe do lead: codigo e botoes existem, mas nao ha E2E especifico nesta auditoria.
* Rotas `PUT`/`DELETE` de leads, clientes, propostas e tarefas: existem no backend, mas nao foram exercitadas uma a uma por interface.
* Revogacao de consentimento: rota existe, mas nao ha tela nem teste E2E.
* Fluxo parceiro completo em UI: backend testado, mas navegacao visual como parceiro nao foi validada rota a rota.
* Logs de producao Render/Vercel: nao validados por falta de acesso ao painel.

## 7. O que esta incompleto

* Treinamentos sao arrays estaticos no frontend.
* Evolution API esta somente preparada em simulacao, sem cliente real, timeout, retry ou health check externo.
* Admin nao cria, edita, desativa usuario nem altera configuracoes.
* Nao ha upload de documentos.
* Nao ha exportacao/relatorios operacionais.
* Nao ha recuperacao de senha.
* Nao ha multi-tenant SaaS.
* Nao ha criptografia de campos pessoais em repouso.
* Nao ha frontend para revogar consentimento.
* Nao ha cobertura E2E para todas as telas e botoes.

## 8. O que esta quebrado

* Acao executada: varredura Playwright em `/login`.
* Resultado esperado: pagina abrir sem erros de console.
* Resultado obtido: pagina abriu e funcionou, mas apareceu um erro de console `Failed to load resource: the server responded with a status of 404 (Not Found)`.
* Arquivo/linha provavel: nao identificado; possivel asset/favico ausente servido pelo Vite.
* Gravidade: Baixa, nao bloqueia fluxo.

Nao houve erro reproduzivel bloqueando build, testes, login, API principal ou navegacao.

## 9. O que ainda nao existe

* Recuperacao de senha.
* MFA.
* Sessao por cookie HttpOnly/Secure/SameSite.
* Controle SaaS multi-tenant.
* Upload e gestao documental.
* Integracoes reais INSS, FGTS, bancos, Bacen, Consig360, Kardbank, Evolution API real.
* Pagamento/cancelamento.
* Exportacao CSV/PDF.
* Webhooks com assinatura.
* Rotina visivel de backup/restore.
* Monitoramento/alertas integrados.
* Painel administrativo completo.

## 10. Banco de dados

Banco atual: SQLite em `backend/app.db`.

Tabelas encontradas e persistindo: `users` 4, `leads` 41, `clientes` 87, `propostas` 7, `tarefas` 4, `whatsapp_messages` 83, `audit_logs` 731, `consents` 82, `simulations` 45, `schema_migrations` 5.

Persistencia real local comprovada: clientes, consentimentos, mensagens WhatsApp simuladas, simulacoes, auditoria, soft delete de cliente e usuarios demo.

Simulacao: INSS/FGTS usam regras demonstrativas centralizadas; WhatsApp registra historico interno sem envio real; propostas usam banco/produto/valores ficticios.

Migrations existem em `backend/migrations`, separadas para SQLite e PostgreSQL. O codigo ainda usa `Base.metadata.create_all` como bootstrap local/controlado, documentado como inadequado para producao real.

Riscos de banco: SQLite no deploy controlado, ausencia de criptografia em repouso, soft delete aplicado em clientes mas nao em todas as tabelas com dados pessoais, consentimentos sem FK formal no modelo, dados de teste acumulados.

## 11. Integracoes

| Integracao | Finalidade | Onde | Variavel | Estado | Validacao | Status |
|---|---|---|---|---|---|---|
| Evolution API | WhatsApp futuro | `Admin.tsx`, `routes/whatsapp.py`, docs | `EVOLUTION_API_MODE`, `EVOLUTION_API_URL`, `EVOLUTION_API_TOKEN` | Simulada | E2E registrou simulacao sem envio real | FUNCIONA como simulacao |
| INSS | Consulta demonstrativa | `services/simulations.py` | N/A | Simulada | API 200 e pytest snapshot | FUNCIONA como simulacao |
| FGTS | Consulta demonstrativa | `services/simulations.py` | N/A | Simulada | API 200 | FUNCIONA como simulacao |
| Supabase/PostgreSQL | Banco futuro/migrations | docs, scripts, workflows | `DATABASE_URL`, `DIRECT_URL`, `SUPABASE_DIRECT_URL` | Preparado, nao ativo local | testes de script/workflow passaram | PRONTO, MAS NAO VALIDADO em banco real |
| Render | Backend publicado | `render.yaml`, URL publica | envs Render | Ativo controlado | `/healthz` 200 apos retry | FUNCIONA PARCIALMENTE |
| Vercel | Frontend publicado | `frontend/vercel.json`, URL publica | `VITE_API_URL` | Ativo | `/login` 200 e login demo OK | FUNCIONA |

## 12. Seguranca e LGPD

Criticos para producao real:
* SQLite e ausencia de criptografia em repouso para dados pessoais.
* Sessao via Bearer token em localStorage, sem cookies HttpOnly/Secure.
* Nao ha multi-tenant; nao pode ser tratado como SaaS real.
* Usuarios/senhas demo aparecem na tela de login por design.

Importantes:
* `BBB_AUTH_SECRET` tem fallback demo se ambiente local nao configurar.
* Rate limit e em memoria; nao serve para escala multi-instancia.
* Sem MFA, recuperacao de senha, politica robusta de sessao ou refresh token.
* Consentimento existe para WhatsApp, mas revogacao nao tem UI.
* Soft delete nao esta padronizado para todas as tabelas sensiveis.

Melhorias:
* Migrar `@app.on_event` para lifespan FastAPI.
* Usar datas timezone-aware.
* Adicionar testes E2E por tela e por permissao.
* Investigar 404 de recurso no login.
* Reduzir bundle frontend ou aplicar code splitting.

Varredura de segredos: nao encontrei padrao de chave real. Foram encontrados apenas placeholders, segredos demo e URLs ficticias em testes/docs. Valores sensiveis reais nao foram impressos.

## 13. Os 12 riscos Yntelli

| Regra | Status | Evidencia | Gravidade |
|---|---|---|---|
| 1. Regras de negocio espalhadas | Parcial | regras de produto em `business_rules`, mas status/listas tambem no frontend | Media |
| 2. Troca de ferramenta sem ADR | OK | ADRs 001-013 cobrem banco, backend, frontend, auth, deploy | Baixa |
| 3. Resquicios de projeto copiado | OK | `referencias/` documentado como inspiracao; codigo proprio | Baixa |
| 4. Arquivos >500 linhas | OK | nenhum arquivo fonte >500 linhas fora deps/build | Baixa |
| 5. Banco sem desenho atualizado | Parcial | docs e migrations existem; PostgreSQL futuro ainda nao validado real | Media |
| 6. Operacoes lentas travando requisicoes | Nao validado | sem teste de carga; consultas simples | Media |
| 7. Ausencia de AGENTS.md | OK | `AGENTS.md` existe | Baixa |
| 8. Dados pessoais sem protecao | Atencao | mascaramento por perfil existe; sem criptografia em repouso | Alta |
| 9. APIs externas sem cache/retry | Parcial | integracoes reais nao existem; futura Evolution sem modulo real | Media |
| 10. Margem/regra fixa no codigo | Parcial | regras demo centralizadas, mas valores ficticios fixos | Media |
| 11. Comunicacao sem consentimento | OK no simulado | WhatsApp bloqueia sem opt-in; pytest comprovou 403 | Baixa |
| 12. Simulacao sem historico/prova | OK no MVP | `simulations` tem snapshot/hash; pytest comprovou | Baixa |

## 14. Prioridades de recuperacao

### CRITICOS

* Manter bloqueio de dados reais ate PostgreSQL gerenciado, criptografia em repouso, backup/restore, monitoramento e revisao LGPD.
* Fortalecer autenticacao para producao: cookies seguros ou desenho equivalente, segredo obrigatorio, expiracao/refresh, politica de senha e opcional MFA.
* Definir isolamento multi-tenant antes de qualquer posicionamento SaaS real.

### IMPORTANTES

* Completar UI de CRUD: editar/excluir/status para leads, propostas, tarefas e clientes conforme permissao.
* Criar gestao de usuarios no Admin.
* Adicionar UI para revogar consentimento.
* Cobrir LeadDetail, propostas, tarefas, INSS, FGTS, admin e parceiro com E2E.
* Investigar 404 de recurso no login e bundle >500 kB.

### MELHORIAS

* Transformar treinamentos em modulo editavel.
* Adicionar exportacao/relatorios.
* Adicionar code splitting.
* Migrar FastAPI startup para lifespan e datas UTC timezone-aware.
* Criar health check interno para integracoes futuras.

## 15. Proxima acao recomendada

Menor sequencia segura:

1. Congelar escopo como MVP controlado com dados ficticios.
2. Corrigir gaps de UI ja suportados pelo backend: editar/status/excluir e revogacao de consentimento.
3. Ampliar E2E para todas as telas e perfis.
4. Corrigir seguranca de sessao antes de qualquer dado real.
5. Validar PostgreSQL gerenciado em ambiente separado, com migrations formais e backup/restore.
6. So depois discutir integracoes reais e operacao SaaS.

AUDITORIA CONCLUIDA

* Nenhum codigo foi alterado.
* Nenhuma publicacao foi realizada.
* Nenhum dado real foi disparado.
* Relatorio salvo em: docs/audit/INVESTIGATION_FUNCTIONAL_2026-07-12.md

PROXIMO PASSO DO ALUNO:

Copiar todo este relatorio e colar na conversa com o Arquiteto Yntelli para receber um unico plano seguro de recuperacao.
