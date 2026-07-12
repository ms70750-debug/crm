# ADR 012 - Backup E Restauracao

Status: APROVADO.

Data da aprovacao: 2026-07-12.
Aprovado pelo dono do projeto.
Escopo: USO PROPRIO.
Observacao: ativacao real depende de auditoria final, credenciais seguras e aprovacao explicita para publicacao.

## Contexto

Dados reais exigem backup diario, retencao, teste de restore e separacao clara entre demo e producao.

## Decisao

Criar scripts seguros e nao destrutivos para backup/restore ficticio local e documentar a rotina obrigatoria para provedor gerenciado. Nenhum backup real sera configurado nesta tarefa.

## Alternativas

- Confiar somente no provedor: simples, mas pouco auditavel.
- Backup proprio sem criptografia: proibido para dados reais.
- Backup gerenciado + teste de restore: caminho recomendado.

## Riscos

- Backup sem restore testado pode ser inutil.
- Retencao excessiva viola minimizacao LGPD.
- Backup com segredo exposto vira vazamento.

## Reversao

Desabilitar modo de dados reais e manter apenas banco demo local.

## Criterio De Aprovacao

Backup externo configurado, criptografado, monitorado, com restore testado e plano de rollback documentado.

## Impacto Operacional

Exige janela de verificacao, responsavel por incidentes, alertas e revisao de retencao.
