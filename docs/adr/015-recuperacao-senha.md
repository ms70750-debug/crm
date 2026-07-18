# ADR 015 - Recuperacao segura de senha

## Contexto

O CRM BBB Consig nao possui cadastro publico e o login demo publico permanece bloqueado fora de modo demo. A tela de login oferecia apenas contato manual para recuperacao, o que nao permitia redefinir senha por token.

## Decisao

Criar um fluxo de recuperacao com token aleatorio, hash SHA-256 persistido e uso unico. O token usa o proposito `password_recovery`, separado de `first_admin_activation`, e nao pode ser aceito pelos endpoints de ativacao administrativa.

O endpoint de solicitacao responde de forma neutra para e-mails existentes ou inexistentes. O CRM prepara o link para entrega segura fora do aplicativo, mas nao envia e-mail real nesta etapa.

## Consequencias

- Senha nova exige a mesma politica forte usada na ativacao de admin.
- Ao redefinir senha, sessoes ativas do usuario sao revogadas.
- Logs de auditoria nao registram token aberto, hash de token, senha ou secret.
- A variavel `PASSWORD_RECOVERY_BASE_URL` define a URL publica usada na montagem do link.
