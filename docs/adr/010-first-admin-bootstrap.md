# ADR 010 - Fluxo de primeiro administrador real

Status: aceito

Data: 2026-07-15

## Contexto

O CRM BBB Consig bloqueia login demo publico e nao possui cadastro publico de usuarios. Para liberar uso real, o proprietario precisa ativar o primeiro administrador real sem senha padrao, sem token em chat, sem token em logs e sem acesso direto ao banco.

## Decisao

Criar um fluxo oficial, auditado e de uso unico para ativacao administrativa. O fluxo usa token aleatorio, grava somente o hash SHA-256 do token no banco e entrega o link privado exclusivamente por artifact do GitHub Actions. O proprietario define a propria senha na pagina `/ativar-admin`.

Nao havera cadastro administrativo publico. A criacao do primeiro administrador real so sera permitida quando nao existir outro administrador real ativo. Usuarios demo com dominio `.demo` nao contam como administrador real.

## Alternativas Consideradas

- Criar senha temporaria manualmente: rejeitado porque exporia credencial operacional.
- Inserir usuario diretamente no banco: rejeitado porque contorna a camada auditada do projeto.
- Reativar login demo: rejeitado por risco de bypass publico.
- Convite por e-mail automatico: adiado porque nao ha provedor de e-mail transacional configurado.

## Riscos

- Vazamento do artifact permitiria uso do link enquanto valido.
- Link expirado exige nova execucao manual do workflow.
- Se outro administrador real existir, o fluxo bloqueia para evitar tomada indevida da conta.

## Expiracao

Tokens expiram em no maximo 60 minutos. Tokens expirados nao podem ser consumidos.

## Uso Unico

O token e marcado como usado na mesma operacao de ativacao. Outros tokens pendentes do mesmo e-mail sao invalidados.

## Auditoria

Criacao, bloqueio e consumo do token registram audit log com e-mail mascarado e sem token, hash ou senha.

## Plano de Reversao

A reversao remove o fluxo de ativacao e a tabela `admin_bootstrap_tokens` apenas se nenhum token ativo depender dela. O merge e protegido por tag `pre-merge-first-admin-bootstrap-2026-07-15`.

## Criterio de Revisao

- Nenhum token aberto persistido no banco.
- Nenhum token ou senha em logs, summary ou commit.
- Workflow manual somente na `main`.
- Artifact com retencao de 1 dia.
- Login demo segue bloqueado.
- Ativacao cria ou promove somente o e-mail autorizado pelo token.
