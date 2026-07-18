# Checklist de Ativacao Real - BBB Consig CRM

Este checklist prepara a ativacao, mas nao autoriza dados reais sozinho.

## Antes de habilitar dados reais
- Confirmar classificacao `USO_PROPRIO`.
- Confirmar projeto Supabase correto e vazio ou sem dados inesperados.
- Configurar secrets somente nos paineis seguros.
- Aplicar migrations PostgreSQL por workflow manual confirmado.
- Executar restore isolado aprovado.
- Confirmar backup automatico diario criptografado.
- Confirmar alertas de Render, Vercel, Supabase e GitHub Actions.
- Revisar minutas LGPD com profissional habilitado.
- Gerar link de primeiro administrador por canal seguro.

## Chaves de corte
Manter falso/desabilitado ate autorizacao final:
- `REAL_DATA_MODE=false`
- `EVOLUTION_API_MODE=simulation`
- comunicacao real desabilitada
- integrações externas reais desabilitadas

## Voltar ao modo ficticio
1. Definir `REAL_DATA_MODE=false`.
2. Definir `APP_MODE=demo` quando o ambiente voltar a treinamento.
3. Bloquear integracoes reais.
4. Validar `/healthz`.
5. Registrar auditoria da mudanca.
