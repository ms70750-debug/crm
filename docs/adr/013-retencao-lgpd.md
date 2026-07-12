# ADR 013 - Retencao E LGPD

Status: PROPOSTO PARA APROVACAO.

## Contexto

O piloto com dados reais precisa limitar coleta, registrar consentimento, permitir revogacao, aplicar soft delete e evitar logs com dados completos.

## Decisao

Padronizar soft delete, auditoria mascarada, consentimento por canal/finalidade e checklist LGPD antes de ativar dados reais.

## Alternativas

- Excluir fisicamente imediatamente: reduz dados, mas prejudica auditoria e recuperacao.
- Reter indefinidamente: operacionalmente facil, mas arriscado.
- Soft delete + retencao documentada: equilibrio inicial para piloto.

## Riscos

- Politica de retencao incompleta pode manter dados alem do necessario.
- Falta de treinamento pode levar a insercao indevida de dados reais antes da aprovacao.
- Restauracao administrativa deve ser restrita.

## Reversao

Manter `APP_MODE=demo` e dados ficticios ate a politica ser aprovada.

## Criterio De Aprovacao

Politica aprovada pelo dono, consentimento testado, logs mascarados, restore administrativo auditado e revisao LGPD concluida.

## Impacto Operacional

Exige rotina de atendimento a titulares, revogacao de consentimento e auditoria periodica.
