# Checklist Pre-Deploy Controlado

Use antes de qualquer publicacao online.

## Codigo
- [ ] `git status` sem arquivos pendentes.
- [ ] `.env`, `app.db`, backups, logs, `dist`, `node_modules`, `test-results` e `referencias/` fora do Git.
- [ ] Ultimo commit revisado.

## Validacao
- [ ] `backend\.venv\Scripts\python.exe -m pytest backend\tests -q`
- [ ] `npm audit --audit-level=moderate`
- [ ] `npm run build`
- [ ] `npm run e2e`
- [ ] `GET /healthz` responde `status: ok`.

## Ambiente
- [ ] `BBB_AUTH_SECRET` criado no painel do provedor, sem valor real em arquivo.
- [ ] `CORS_ORIGINS` limitado ao dominio do frontend.
- [ ] `VITE_API_URL` aponta para o backend correto.
- [ ] `EVOLUTION_API_MODE=simulation`.
- [ ] WhatsApp, INSS, FGTS e bancos continuam sem integracao real.

## Banco
- [ ] SQLite usado apenas para teste controlado.
- [ ] Nenhum dado real publicado.
- [ ] Plano PostgreSQL documentado para etapa futura.

## LGPD e Operacao
- [ ] Perfis revisados.
- [ ] Visualizacao de dados sensiveis validada por perfil.
- [ ] Audit log e logs tecnicos sem CPF completo desnecessario.
- [ ] Opt-in de comunicacao preservado.
