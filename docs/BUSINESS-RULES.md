# Regras de Negocio

## BR-001 Classificacao do ambiente
O sistema esta classificado como USO_PROPRIO - MVP CONTROLADO. E permitido somente uso com dados ficticios ou anonimizados ate nova aprovacao formal.

## BR-002 Cadastro e gestao de cliente
Clientes devem ser criados com dados ficticios no ambiente demo/controlado. Dados pessoais devem ser removidos apenas por soft delete quando aplicavel.

## BR-003 Visualizacao operacional por perfil
Admin, supervisor e operador podem visualizar CPF, telefone, email, beneficio, matricula, convenio, banco de pagamento e observacoes operacionais completos quando isso for necessario para atendimento interno.

## BR-004 Limitacao do perfil parceiro
Parceiro deve visualizar apenas dados atribuidos a ele e com CPF, telefone e email mascarados ou limitados. Parceiro nao deve acessar dados administrativos nem clientes nao atribuidos.

## BR-005 Mascaramento em logs e relatorios
Audit logs, logs tecnicos, respostas de erro e dashboards agregados nao devem expor CPF, telefone ou email completos quando o dado individual nao for indispensavel.

## BR-006 Simulacao INSS
Simulacao INSS usa regras demonstrativas centralizadas. Resultado nao vale como proposta real.

## BR-007 Simulacao FGTS
Simulacao FGTS usa regras demonstrativas centralizadas. Resultado nao vale como proposta real.

## BR-008 Registro de WhatsApp simulado
WhatsApp registra somente historico interno. Nenhuma mensagem real e enviada nesta fase.

## BR-009 Opt-in obrigatorio antes de comunicacao
Qualquer registro de comunicacao por WhatsApp exige consentimento ativo do cliente para o canal.

## BR-010 Snapshot de simulacao
Toda simulacao deve gerar snapshot com dados usados, regra aplicada, resultado, timestamp e hash SHA-256.

## BR-011 Regras demonstrativas
Taxas, margens e convenios sao ficticios. Nao usar para proposta real sem validacao comercial.

## BR-012 Proibicao de dados reais nesta fase
Nao inserir CPF real, conta bancaria real, beneficio real, margem real ou contrato real enquanto o projeto estiver em MVP controlado.

## BR-013 Modo demonstracao obrigatorio
Enquanto `APP_MODE=demo`, o sistema deve exibir aviso visivel e bloquear CPFs matematicamente validos em cadastros e simulacoes. CPFs ficticios/invalidos continuam permitidos para teste.

## BR-014 Login de demonstracao
Usuarios de demonstracao podem ser usados somente em `APP_MODE=demo`. A interface nao deve exibir senhas demo. O login demo por perfil serve apenas para validacao controlada.

## BR-015 Comunicacao simulada e opt-out
WhatsApp permanece simulado. O registro de mensagem exige opt-in ativo e deve permitir opt-out/revogacao de consentimento sem enviar comunicacao real.

## BR-016 Producao real e SaaS bloqueados
Dados reais, integracoes reais, multi-tenancy e operacao SaaS dependem de decisao comercial explicita, ADRs, isolamento, revisao LGPD, auditoria e aprovacao antes de qualquer uso.
