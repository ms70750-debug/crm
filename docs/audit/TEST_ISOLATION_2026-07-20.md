# Auditoria de Isolamento de Testes - 2026-07-20

## Causa comprovada

O check-up semanal executou a suite backend com `session.py` usando o fallback persistente `backend/app.db`. Esse arquivo continha um administrador real local, e os testes de bootstrap esperavam banco descartavel sem administrador real. A fixture limpava apenas usuarios de dominio de teste, portanto o administrador persistente interferiu em sete casos.

## Testes afetados

- Criacao e ativacao do primeiro administrador.
- Promocao de usuario comum por token.
- Recuperacao do mesmo administrador sem duplicidade.
- Rejeicao de tokens invalidos, expirados e usados.
- Validacao de expiracao UTC restaurada.
- Rejeicao de senha fraca/divergente e rate limit.
- Endpoint de ativacao com sessao segura.

## Protecao implementada

- `APP_ENV=test` passa por guarda fail-closed antes do engine SQLAlchemy.
- Supabase, Render, Vercel, hosts publicos e SQLite persistente sao rejeitados.
- Secrets de producao nao podem estar presentes no processo de teste.
- Cada execucao recebe `BBB_TEST_RUN_ID`.
- Testes locais usam banco temporario exclusivo quando nenhum `DATABASE_URL` descartavel e fornecido.
- CI usa PostgreSQL 17 descartavel como service container.

## E2E e smoke

- `npm run e2e:disposable` continua autorizado a criar dados sinteticos apenas em ambiente local descartavel.
- `npm run smoke:production` e separado e bloqueia metodos de escrita.
- O smoke de producao nao recebe credenciais administrativas.

## Garantias

- Nenhum teste precisa acessar Supabase oficial.
- Nenhum teste precisa de secrets do Render, Vercel, Supabase ou Resend.
- Nenhum cliente, lead, proposta, consentimento ou sessao e criado em producao.
- Nenhuma conexao, senha, hash, token, cookie ou fingerprint foi registrada neste documento.
