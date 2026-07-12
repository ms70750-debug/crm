# LGPD

Status: PROPOSTO PARA APROVACAO. Dados reais continuam proibidos.

## Principios Aplicados

- Minimizar coleta.
- Mascarar logs.
- Exigir consentimento ativo para comunicacao.
- Permitir opt-out.
- Usar soft delete antes de exclusao definitiva.
- Preparar criptografia em repouso para campos sensiveis com envelope versionado e Fernet.

## Dados Sensíveis

CPF, telefone, email, beneficio, dados bancarios, observacoes com dados pessoais e identificadores financeiros devem ser protegidos antes de qualquer piloto real.

## Controles Implementados Como Fundacao

- Bloqueio de CPF matematicamente valido em demo.
- Audit log com sanitizacao.
- Consentimento com finalidade, status e revogacao.
- Soft delete e restauracao administrativa auditada para cliente.
- Readiness bloqueando `APP_MODE=production` sem controles obrigatorios.

## Pendencias Para Uso Real

- Aprovar ADRs 009 a 013.
- Provisionar chave real fora do Git.
- Definir politica de retencao.
- Testar backup/restore externo.
- Fazer auditoria final.
