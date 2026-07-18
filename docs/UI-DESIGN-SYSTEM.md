# Sistema Visual BBB Consig CRM

## Referencia
- Fonte visual: site oficial `https://www.bbbemprestimos.com.br/`.
- Ativos locais: `frontend/public/brand/logo-bbb-consig-oficial.jpeg` e `frontend/public/brand/arte-bbb-consig-horizontal.png`.
- Nao ha copia de codigo do site oficial; o CRM apenas usa a linguagem visual e ativos institucionais publicados pelo dominio da empresa.

## Paleta
- Azul institucional: `#0b5ed7`.
- Azul escuro: `#0b3c86`.
- Emerald de sucesso/acoes seguras: `#10b981`.
- Dourado de atencao leve: `#f8c545`.
- Grafite de texto: `#0f2143`.
- Linha: `#dbe5f2`.
- Fundo: `#f8fbff`.
- Superficie: `#ffffff`.

## Componentes
- `Layout`: sidebar branca, logo oficial, item ativo azul e cabecalho fixo claro.
- `Panel`: card operacional branco com borda suave e raio de 8px.
- `input`: campo claro com foco azul institucional.
- `btn`: acao primaria azul, com texto branco e altura minima estavel.
- `btn-secondary`: acao secundaria branca com borda e hover azul.
- `badge`: etiquetas retangulares de raio baixo para status e metadados.
- `subtle-card`: bloco interno off-white para listas, timelines e informacoes resumidas.
- `alert-success` e `alert-error`: estados sem dependencia de cor escura.

## Regras de uso
- Manter todos os fluxos com dados ficticios enquanto o projeto estiver em modo controlado.
- Nao usar assets remotos em runtime para identidade visual.
- Evitar paginas promocionais dentro do CRM; a primeira tela apos login deve continuar sendo operacional.
- Preservar contraste alto em tabelas, formularios e badges.
- Manter raio de cards em ate 8px, salvo imagens da marca.
