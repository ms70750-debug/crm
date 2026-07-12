# LGPD

Status: ADRs 009 a 013 APROVADOS para USO PROPRIO. Dados reais continuam proibidos ate auditoria LGPD final e aprovacao explicita do dono.

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

- Provisionar chave real fora do Git.
- Definir politica de retencao.
- Testar backup/restore externo.
- Fazer auditoria LGPD final.
- Obter aprovacao explicita para publicacao e uso real.
