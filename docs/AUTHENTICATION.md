# Autenticacao e Recuperacao

## Estado atual

O CRM usa usuarios internos, sessoes server-side e cookie HttpOnly. Em producao controlada, o cookie deve ser `Secure` e `SameSite=None`.

Login demo e permitido somente quando `APP_MODE=demo`, `PUBLIC_DEMO_LOGIN_ENABLED=true` e fora de `APP_MODE=production`.

## Primeiro administrador

O primeiro administrador real deve ser ativado por link temporario e de uso unico. O token aberto nunca deve ser persistido, logado, publicado em PR ou copiado para relatorio. A tabela `admin_bootstrap_tokens` guarda apenas hash, proposito, expiracao e uso.

Fluxo seguro:
1. Confirmar PostgreSQL persistente.
2. Aplicar migrations formais.
3. Confirmar que nao existe administrador real ativo.
4. Gerar link de ativacao com proposito `first_admin_activation`.
5. Entregar por artifact privado ou e-mail transacional validado.
6. O usuario define a propria senha.

## Recuperacao de senha

A solicitacao de recuperacao responde de forma neutra para conta existente ou inexistente. Se a conta existir e estiver ativa, o backend cria token com proposito `password_recovery`, expira em janela curta e invalida tokens anteriores da mesma finalidade.

Ao redefinir senha, sessoes antigas sao revogadas. Token de recuperacao nao ativa administrador, e token de ativacao nao redefine senha.

## E-mail transacional

O provedor preparado e Resend. Variaveis por nome:
- `AUTH_EMAIL_ENABLED`
- `AUTH_EMAIL_MODE`
- `AUTH_EMAIL_FROM`
- `APP_PUBLIC_URL`
- `RESEND_API_KEY`

Padrao seguro:
- `AUTH_EMAIL_ENABLED=false`
- `AUTH_EMAIL_MODE=simulate`

Envio real exige conta, dominio/remetente e secret configurados em ambiente seguro. Erros do provedor nao devem revelar se a conta existe.
