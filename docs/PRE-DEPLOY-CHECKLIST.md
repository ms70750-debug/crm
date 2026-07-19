# Checklist Pre-Deploy Controlado

Use antes de qualquer publicacao online.

## Corte para producao real
- [ ] Confirmar classificacao `USO_PROPRIO`.
- [ ] Confirmar PostgreSQL/Supabase correto.
- [ ] Rodar migrations PostgreSQL em ambiente isolado.
- [ ] Executar restore isolado aprovado.
- [ ] Manter `REAL_DATA_MODE=false` ate autorizacao final.
- [ ] Manter `EVOLUTION_API_MODE=simulation` ate autorizacao de comunicacao real.
- [ ] Confirmar alertas e canal de incidente.
- [ ] Confirmar revisao juridica das minutas LGPD.

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
- [ ] `APP_ENV=production` configurado no provedor para validar ambiente.
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
