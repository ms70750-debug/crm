# Checklist de Ativacao Real - BBB Consig CRM

Este checklist prepara a ativacao, mas nao autoriza dados reais sozinho.

## Antes de habilitar dados reais
- Confirmar classificacao `USO_PROPRIO`.
- Confirmar projeto Supabase correto e vazio ou sem dados inesperados.
- Configurar secrets somente nos paineis seguros.
- Aplicar migrations PostgreSQL por workflow manual confirmado.
- Executar restore isolado aprovado.
- Confirmar backup automatico diario criptografado.
- Confirmar alertas de Render, Vercel, Supabase e GitHub Actions.
- Revisar minutas LGPD com profissional habilitado.
- Gerar link de primeiro administrador por canal seguro.

## Sequencia final sem acesso a Locaweb

Esta lista deve ser executada somente depois que o acesso DNS estiver disponivel. Nao executar parcialmente.

1. Acessar Locaweb.
2. Adicionar os registros DNS informados pelo Resend para `auth.bbbemprestimos.com.br`.
3. Aguardar o Resend marcar dominio e remetente como verificados.
4. Criar chave Resend restrita a envio.
5. Salvar `RESEND_API_KEY` apenas nos paineis seguros.
6. Confirmar `AUTH_EMAIL_ENABLED=false` e `AUTH_EMAIL_MODE=simulate`.
7. Confirmar backup pre-migration criptografado do Supabase principal.
8. Confirmar restore em PostgreSQL descartavel.
9. Aplicar migrations aditivas no Supabase vazio.
10. Validar auditoria readonly e permissoes.
11. Mergear PR #32.
12. Configurar Render com PostgreSQL persistente e acionar um unico deploy.
13. Validar Vercel no commit da `main`.
14. Criar exatamente um administrador real pendente, sem senha criada pelo sistema.
15. Habilitar e-mail transacional apenas para enviar um unico link de ativacao.
16. Aguardar o usuario definir a propria senha pelo link.
17. Habilitar `REAL_DATA_MODE=true` somente depois de login, persistencia, backup e monitoramento aprovados.

## Chaves de corte
Manter falso/desabilitado ate autorizacao final:
- `REAL_DATA_MODE=false`
- `EVOLUTION_API_MODE=simulation`
- comunicacao real desabilitada
- integrações externas reais desabilitadas

## Voltar ao modo ficticio
1. Definir `REAL_DATA_MODE=false`.
2. Definir `APP_MODE=demo` quando o ambiente voltar a treinamento.
3. Bloquear integracoes reais.
4. Validar `/healthz`.
5. Registrar auditoria da mudanca.
