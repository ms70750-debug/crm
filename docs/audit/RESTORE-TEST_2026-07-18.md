# Restore Test - 2026-07-18

## Escopo
Teste preparado para ambiente isolado e descartavel, sem clientes reais e sem restaurar sobre homologacao ou producao.

## Resultado desta tarefa
Restore real em Supabase isolado nao foi executado porque nao ha conector/credencial segura disponivel nesta sessao para criar ou acessar projeto descartavel sem senha, 2FA ou possivel custo. O trabalho tecnico local validou backup/restore ficticio e scripts de backup criptografado por testes automatizados.

## Procedimento aprovado para execucao manual segura
1. Criar banco PostgreSQL vazio e descartavel.
2. Configurar `POSTGRES_RESTORE_URL` somente em secret/ambiente seguro.
3. Gerar backup criptografado do banco isolado.
4. Validar checksum.
5. Descriptografar somente no runner seguro.
6. Restaurar no segundo banco descartavel.
7. Validar schema, tabelas, indices, constraints, login sintetico, cliente ficticio, audit log e soft delete.
8. Descartar bancos temporarios.

## Evidencias locais
- Testes automatizados validam criptografia, checksum, mascaramento de URL e remocao de arquivo aberto.
- Teste ficticio SQLite valida geracao e restauracao local sem dados reais.
- Nenhum banco principal foi alterado.

## Duracao
Nao medida em Supabase isolado nesta tarefa. RTO observado local fica limitado ao teste automatizado de restore ficticio.

## RPO esperado
24 horas para rotina diaria minima enquanto o workflow permanecer diario.

## RTO alvo
Definir apos primeiro restore isolado Supabase completo. Alvo inicial recomendado para USO_PROPRIO: ate 4 horas.

## Limitacoes
- Sem credenciais reais exibidas.
- Sem projeto isolado criado por falta de acesso seguro nesta sessao.
- Sem uso de dados reais.
