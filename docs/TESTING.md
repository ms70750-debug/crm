# Testes - BBB Consig CRM

## Ambientes

Producao, teste backend, E2E descartavel e smoke publico sao fluxos separados.

- Producao: somente leitura em smoke; sem credenciais administrativas; sem escrita.
- Backend test: `APP_ENV=test`, banco exclusivo da execucao e `REAL_DATA_MODE=false`.
- E2E descartavel: backend local, frontend local, dados sinteticos e banco eliminado ao final.
- Smoke de producao: apenas `GET` e `HEAD` em frontend publico e `/healthz`.

## Guarda de banco em teste

Quando `APP_ENV=test`, a aplicacao valida o destino antes de criar o engine.

Bloqueios:
- Supabase e poolers externos;
- Render, Vercel e URLs publicas;
- SQLite persistente do workspace;
- banco sem identificador descartavel;
- secrets de producao como variaveis de teste.

Permissoes:
- SQLite temporario dentro do diretorio temporario do sistema, com `BBB_TEST_RUN_ID`;
- PostgreSQL local ou service container com nome de banco contendo marcador de teste.

Mensagens de erro sao sanitizadas e nao exibem conexao, host, usuario, senha, token ou fingerprint.

## Backend

Local:

```bash
backend\.venv\Scripts\python.exe -m pytest backend\tests
backend\.venv\Scripts\python.exe -m pytest backend\tests
```

No GitHub Actions, o workflow `Test Isolation` roda a suite backend duas vezes contra PostgreSQL 17 descartavel.

## E2E descartavel

O E2E pode criar cliente sintetico, opt-in, simulacao e outros dados somente contra backend local descartavel.

Comandos:

```bash
cd frontend
npm run e2e:disposable
```

O workflow `Test Isolation` sobe PostgreSQL 17 descartavel, backend local e frontend local antes do Playwright.

## Smoke de producao

O smoke publico e somente leitura:

```bash
cd frontend
npm run smoke:production
```

Esse fluxo bloqueia `POST`, `PUT`, `PATCH` e `DELETE` no proprio teste. Ele valida somente frontend publico, SSL/HTTPS pela navegacao, `/healthz`, `database=ok`, `environment=production` e metadados seguros de e-mail.

## Limpeza

Dados sinteticos de backend e E2E pertencem apenas ao banco descartavel da execucao. Arquivos temporarios ficam fora do repositorio e sao removidos no encerramento do processo ou pelo runner.
