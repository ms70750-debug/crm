# ADR 011 - Criptografia de dados pessoais em repouso

## Status
Proposed

## Contexto
O sistema manipula campos sensiveis, mesmo que atualmente apenas em base ficticia. Para dados reais, controle por perfil e mascaramento nao substituem protecao em repouso.

## Campos sensiveis
- CPF e RG.
- Conta, agencia e banco de pagamento.
- Endereco.
- Beneficio, matricula e dados previdenciarios.
- Observacoes operacionais que contenham dados pessoais.

## Decisao proposta
Definir estrategia de criptografia ou protecao equivalente antes de usar dados reais. A estrategia deve considerar chaves fora do codigo, rotacao, backup, restore, busca por campos criptografados e auditoria.

## Consequencias
- Nenhuma criptografia completa sera implementada nesta etapa sem ADR aprovado.
- Dados reais continuam proibidos no MVP controlado.
- A decisao final deve equilibrar seguranca, operacao e capacidade de atendimento.
