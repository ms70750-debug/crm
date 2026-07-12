# ADR 011 - Autenticacao De Producao

Status: APROVADO.

Data da aprovacao: 2026-07-12.
Aprovado pelo dono do projeto.
Escopo: USO PROPRIO.
Observacao: ativacao real depende de auditoria final, credenciais seguras e aprovacao explicita para publicacao.

## Contexto

O modo demo usa usuarios ficticios e login simplificado. Para dados reais, autenticacao precisa separar demo e producao e falhar com seguranca quando secrets estiverem ausentes ou fracos.

## Decisao

Manter `/auth/demo-login` somente em demo. Em `APP_MODE=production`, exigir segredo forte, cookie HttpOnly Secure, expiracao, rate limit, logout e ausencia de token sensivel em localStorage.

## Alternativas

- Continuar com usuarios demo: inadequado para dados reais.
- Integrar provedor externo de identidade: melhor no futuro, mas fora desta tarefa.
- Autenticacao interna reforcada: caminho minimo para piloto interno controlado.

## Riscos

- Senhas fracas ou compartilhadas podem comprometer o piloto.
- Sessao sem HTTPS nao pode ser aceita.
- Falta de MFA aumenta risco em producao real.

## Reversao

Voltar para `APP_MODE=demo`, mantendo acesso apenas a dados ficticios.

## Criterio De Aprovacao

Secrets fortes configurados, HTTPS validado, demo-login bloqueado, testes de sessao aprovados e politica de usuarios definida pelo dono.

## Impacto Operacional

Exige cadastro e desligamento de usuarios, revisao periodica de acesso e procedimento de reset seguro.
