# ADR 014 - Backup externo criptografado

Status: APROVADO

Data: 2026-07-12

Aprovado pelo dono do projeto

Escopo: USO PROPRIO

## Contexto

O projeto CRM BBB CONSIG usa Supabase no plano Free como banco PostgreSQL futuro para uso proprio. Nesse plano, backup automatico gerenciado pode nao estar disponivel. O banco ja possui migrations estruturais aplicadas, arquitetura BACKEND-ONLY e grants diretos removidos de `PUBLIC`, `anon` e `authenticated`.

Dados reais continuam proibidos ate aprovacao final. Esta ADR nao autoriza backup real, armazenamento externo real, publicacao, agendamento ou uso de dados pessoais reais.

## Decisao proposta

Adotar uma fundacao de backup externo criptografado com:

- `pg_dump` em formato logico custom (`-Fc`) para permitir restore com `pg_restore`.
- Criptografia autenticada antes de qualquer armazenamento.
- Checksum SHA-256 do dump aberto e do arquivo criptografado.
- Manifesto seguro sem credenciais e sem conteudo de clientes.
- Retencao inicial documentada:
  - 7 backups diarios;
  - 4 semanais;
  - 3 mensais.
- Teste mensal de restauracao em PostgreSQL temporario.
- Armazenamento externo ainda nao ativado.
- Nenhuma chave no Git.

## Pendencias mantidas

- Armazenamento externo real ainda pendente.
- Primeiro backup real ainda pendente.
- Restore real controlado ainda pendente.
- Agendamento ainda pendente.
- Dados reais continuam proibidos ate nova aprovacao explicita.

## Riscos

- Perda da chave de criptografia torna backups inutilizaveis.
- Backup logico pode falhar se roles/extensoes necessarias nao forem recriadas no ambiente de restore.
- Plano Free nao substitui estrategia profissional de backup gerenciado.
- Artifacts do GitHub Actions devem ter retencao curta e conter apenas arquivos criptografados.
- Restauracao incompleta pode gerar falsa sensacao de seguranca se nao validar tabelas, migrations, indices, constraints e permissoes.

## Reversao

Como esta ADR apenas propoe a fundacao tecnica, a reversao e remover scripts, workflows e documentacao antes do merge. Depois de aprovada, qualquer alteracao de estrategia deve ser registrada em nova ADR.

Rollback de banco real nao e autorizado por esta ADR.

## Rotacao de chave

A rotacao futura deve:

1. Criar nova `BACKUP_ENCRYPTION_KEY` em secret seguro.
2. Fazer backup novo com a chave nova.
3. Testar restore do backup novo em PostgreSQL temporario.
4. Manter a chave antiga enquanto existirem backups antigos dentro da retencao.
5. Descartar backups antigos somente conforme politica de retencao aprovada.

## Perda da chave

Se a chave for perdida:

- backups criptografados existentes devem ser considerados irrecuperaveis;
- o sistema deve permanecer bloqueado para dados reais ate existir novo backup validado;
- deve ser registrado incidente operacional;
- uma nova chave deve ser criada apenas em ambiente seguro.

## Custo

A etapa inicial nao ativa armazenamento externo real. Custos futuros dependem do provedor escolhido, volume do dump, frequencia, retencao e transferencia.

## Limite do plano Free

O plano Free do Supabase nao deve ser tratado como substituto de backup gerenciado. A solucao proposta reduz risco operacional, mas nao elimina a necessidade futura de plano pago ou backup gerenciado quando houver dados reais relevantes.

## Criterios para mudar para backup gerenciado

Migrar para backup gerenciado quando ocorrer qualquer item:

- uso real com dados pessoais aprovado;
- volume de dados ou criticidade operacional aumentar;
- necessidade de RPO/RTO formal;
- necessidade de suporte, PITR ou snapshots automaticos;
- custo operacional do backup manual superar o custo de plano gerenciado.

## Observacao

Ativacao real depende de auditoria final, credenciais seguras, chave real, armazenamento externo aprovado, restore testado e aprovacao explicita do dono do projeto.
