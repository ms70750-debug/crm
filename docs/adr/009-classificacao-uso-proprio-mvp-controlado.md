# ADR 009 - Classificacao USO_PROPRIO MVP Controlado

## Status
Accepted

## Contexto
O BBB Consig CRM nasceu para uso interno da operacao BBB Consig, com dados ficticios, simulacoes e validacao de fluxo.

## Decisao
Classificar o projeto como USO_PROPRIO - MVP CONTROLADO.

Nesta fase, o sistema nao sera tratado como SaaS e nao exige multi-tenant obrigatorio. O uso permitido fica restrito ao dono da operacao e equipe interna autorizada, com ate 10 usuarios internos e somente dados ficticios ou anonimizados.

## Consequencias
- Nao usar dados reais de clientes.
- Nao vender ou disponibilizar como SaaS.
- Nao exigir isolamento por tenant nesta etapa.
- Reavaliar arquitetura antes de qualquer expansao para terceiros.
