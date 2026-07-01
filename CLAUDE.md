# Instrucoes Para Assistentes Futuros

## Regras de seguranca
- Nunca trabalhar direto na `main` ou versao principal.
- Nunca publicar, fazer deploy ou conectar integracoes reais sem aprovacao explicita.
- Nunca apagar arquivo sem backup em `/backups/<data>/`.
- Nunca usar dados reais no ambiente demo.
- LGPD e mascaramento de dados pessoais sao obrigatorios.

## Produto
- BBB Consig CRM e um CRM demo/local para operacao de consignado.
- WhatsApp, INSS, FGTS e bancos ficam em modo simulacao.
- Interface deve manter tema escuro com detalhes verde/lima.

## Engenharia
- Migrations versionadas ficam em `backend/migrations`.
- Regras de negocio devem ser documentadas em `docs/BUSINESS-RULES.md` e centralizadas em configuracao quando possivel.
- Rodar build/testes antes de commit.
