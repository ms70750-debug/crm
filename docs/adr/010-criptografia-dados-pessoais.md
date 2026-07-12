# ADR 010 - Criptografia De Dados Pessoais

Status: APROVADO.

Data da aprovacao: 2026-07-12.
Aprovado pelo dono do projeto.
Escopo: USO PROPRIO.
Observacao: ativacao real depende de auditoria final, credenciais seguras e aprovacao explicita para publicacao.

## Contexto

O piloto interno com dados reais exige proteger CPF, documentos e dados bancarios em repouso. O repositorio nao pode conter chaves reais.

## Decisao

Criar camada isolada de protecao com envelope versionado, criptografia autenticada por chave em variavel `BBB_DATA_ENCRYPTION_KEY`, hash deterministico separado para CPF e logs mascarados. Esta tarefa prepara a fundacao e mantem dados reais proibidos ate aprovacao final.

## Alternativas

- Criptografar no banco/provedor apenas: reduz codigo, mas nao protege todos os fluxos de aplicacao.
- Criptografar na aplicacao: maior controle, exige gestao de chave.
- Tokenizacao externa: robusta, mas depende de fornecedor e custo.

## Riscos

- Perda da chave impede leitura de dados protegidos.
- Rotacao mal planejada pode indisponibilizar registros.
- Implementacao local deve ser substituida/revisada antes de escala.

## Reversao

Manter `REAL_DATA_MODE=false` e nao gravar dados reais. Campos antigos de demo permanecem operacionais enquanto a migracao real nao for aprovada.

## Criterio De Aprovacao

Chave forte provisionada fora do Git, rotacao documentada, restore validado, testes de criptografia aprovados e auditoria LGPD concluida.

## Impacto Operacional

Exige cofre de secrets, processo de rotacao, backup criptografado e treinamento para nunca expor chaves.
