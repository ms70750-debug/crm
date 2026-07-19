# Monitoramento - BBB Consig CRM

Status: preparado em documentacao e health check seguro. Nao houve contratacao de servico externo nem alteracao de provedor.

## Tentativa de go-live - 2026-07-18

Monitoramento externo real nao foi alterado nesta tentativa. Vercel foi validado por conector autenticado e o backend publico respondeu `/healthz` 200, mas Render nao teve conector/CLI/sessao autenticada disponivel para configurar health check, logs, variaveis de producao ou rollback operacional.

Antes de liberar `REAL_DATA_MODE=true`, confirmar no painel seguro:
- health check do Render apontando para `/healthz`;
- alerta de falha de deploy e indisponibilidade;
- alerta do workflow de backup;
- logs sanitizados sem CPF, e-mail completo, token ou URL de banco;
- responsavel por incidente e canal de contato.

## Backend
- `GET /healthz` deve retornar status do servico, versao, ambiente seguro e status do banco sem revelar secrets.
- O health tambem pode retornar metadados booleanos do e-mail transacional, sem exibir remetente, chave ou dominio sensivel.
- Render deve monitorar `/healthz`.
- Logs devem permanecer sanitizados, sem CPF, conta, agencia, endereco, token ou URL de banco.
- Falhas de autenticacao repetidas devem ser investigadas por audit log e rate limit.
- Falhas de banco devem aparecer como indisponibilidade/degradacao, sem stack trace para usuario final.

## Banco
- PostgreSQL real deve usar SSL obrigatorio, pool controlado e limites de conexao adequados ao plano.
- Alertas desejados: conexoes elevadas, indisponibilidade, armazenamento, lentidao e erro de migration.
- Banco isolado de restore nunca deve ficar publico.

## E-mail transacional
- Enquanto `AUTH_EMAIL_MODE=simulate`, nenhum alerta de entrega real e esperado.
- Ao habilitar Resend, monitorar falhas de envio de ativacao e recuperacao sem registrar e-mail completo, token ou link.

## Frontend
- Vercel deve monitorar disponibilidade do frontend.
- A interface deve tratar API indisponivel com mensagem amigavel e sem stack trace.
- Bundle publico nao deve conter secrets; somente variaveis `VITE_*` nao sensiveis.

## Backup
- GitHub Actions deve sinalizar falha do workflow `Supabase Encrypted Backup`.
- O dono deve revisar falhas de backup antes de qualquer operacao real no dia seguinte.

## Alertas
Sem contratar servico novo automaticamente, usar:
- status/checks do GitHub Actions para backup e migrations;
- health check do Render para backend;
- status do Vercel para frontend;
- painel Supabase para banco, conexoes e armazenamento.

## Pendencias antes da ativacao real
- Confirmar canais de alerta do dono no Render/Vercel/Supabase/GitHub.
- Validar plano com historico de incidentes e escalonamento.
- Registrar pessoa responsavel por resposta a incidente.
