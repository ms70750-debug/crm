# ADR 009 - PostgreSQL Gerenciado Para Piloto Interno

Status: APROVADO.

Data da aprovacao: 2026-07-12.
Aprovado pelo dono do projeto.
Escopo: USO PROPRIO.
Observacao: ativacao real depende de auditoria final, credenciais seguras e aprovacao explicita para publicacao.

## Contexto

O CRM BBB CONSIG usa SQLite no modo demo/controlado. Para um piloto interno com dados pessoais reais, SQLite nao atende aos requisitos de concorrencia, backup gerenciado, observabilidade e operacao segura.

## Decisao

Preparar compatibilidade com PostgreSQL gerenciado via `DATABASE_URL` para runtime e `DIRECT_URL` para migrations/admin. O modo demo continua como padrao seguro. Nenhuma conexao real sera criada nesta tarefa.

## Alternativas

- Manter SQLite: simples, mas inadequado para dados reais.
- Usar PostgreSQL autogerenciado: mais controle, maior risco operacional.
- Usar Supabase/Render Postgres gerenciado: menor operacao inicial e melhor caminho para backup e monitoramento.

## Riscos

- Configuracao incorreta de secrets pode impedir inicializacao.
- Migrations aplicadas sem revisao podem afetar dados.
- Custo e disponibilidade passam a depender do provedor.

## Reversao

Manter `APP_MODE=demo`, `REAL_DATA_MODE=false` e SQLite local. A tag/branch anterior pode ser usada para rollback de codigo.

## Criterio De Aprovacao

Provedor escolhido, `DATABASE_URL`/`DIRECT_URL` configuradas como secrets, dry-run de migrations aprovado, restore testado e auditoria final concluida.

## Impacto Operacional

Exige rotina de migrations, backup, monitoramento, restore testado e controle de acesso aos secrets.
