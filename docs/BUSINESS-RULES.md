# Regras de Negocio

## BR-001 Cadastro e gestao de cliente
Clientes devem ser criados com dados ficticios no ambiente demo. Dados pessoais precisam ser mascarados na interface e removidos apenas por soft delete.

## BR-002 Simulacao INSS
Simulacao INSS usa regras demonstrativas centralizadas. Resultado nao vale como proposta real.

## BR-003 Simulacao FGTS
Simulacao FGTS usa regras demonstrativas centralizadas. Resultado nao vale como proposta real.

## BR-004 Registro de WhatsApp simulado
WhatsApp registra somente historico interno. Nenhuma mensagem real e enviada nesta fase.

## BR-005 Opt-in obrigatorio antes de comunicacao
Qualquer registro de comunicacao por WhatsApp exige consentimento ativo do cliente para o canal.

## BR-006 Mascaramento de CPF na interface
CPF deve aparecer mascarado por padrao como `***.***.123-**` ou equivalente.

## BR-007 Snapshot de simulacao
Toda simulacao deve gerar snapshot com dados usados, regra aplicada, resultado, timestamp e hash SHA-256.

## BR-008 Regras demonstrativas
Taxas, margens e convenios sao ficticios. Nao usar para proposta real sem validacao comercial.
