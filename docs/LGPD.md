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

## Minuta de politica de retencao

Minuta para revisao profissional:
- Leads nao convertidos: revisar retencao periodicamente e excluir/anonimizar quando nao houver finalidade.
- Clientes: manter somente pelo prazo operacional, regulatorio ou contratual aplicavel.
- Consentimentos: preservar historico de concessao/revogacao enquanto necessario para comprovar base legal.
- Audit logs: manter pelo periodo minimo necessario para seguranca e rastreabilidade.
- Backups: reter pelo calendario aprovado e descartar copias vencidas por processo seguro.

## Procedimentos LGPD

### Acesso
Solicitacoes de acesso devem ser registradas em audit log, atendidas por perfil autorizado e entregues por canal seguro.

### Correcao
Correcoes de dados pessoais devem registrar quem alterou, quando alterou e qual entidade foi corrigida, sem expor valores completos em logs.

### Exclusao
Usar soft delete inicialmente. Exclusao definitiva exige aprovacao administrativa, retencao avaliada e registro de auditoria da solicitacao.

### Incidente
Registrar data, origem, impacto estimado, dados potencialmente envolvidos, medidas tomadas e responsavel. Este texto e minuta operacional, nao parecer juridico.
