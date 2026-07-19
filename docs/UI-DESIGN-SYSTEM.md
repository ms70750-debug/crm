# Design System BBB Consig CRM

## Referencia

- Site analisado: `https://www.bbbemprestimos.com.br/`.
- Escopo: adaptar a identidade institucional para uma interface administrativa de CRM.
- Codigo externo copiado: nao.
- Ativos de terceiros copiados: nao.
- Ativos oficiais locais: `frontend/src/assets/brand/bbb-consig-logo.jpeg`, `frontend/src/assets/brand/bbb-consig-banner.png` e `frontend/public/bbb-consig-logo.jpeg`.
- Ativos otimizados locais: `frontend/src/assets/brand/bbb-consig-logo-96.webp`, `frontend/src/assets/brand/bbb-consig-banner-1200.webp` e `frontend/src/assets/brand/bbb-consig-banner-768.webp`.

## Leitura visual

O site oficial usa superficie clara, fundo off-white, textos em grafite, azul institucional forte para chamadas principais, cantos bem arredondados, sombra suave, cards limpos e tipografia Inter. A sensacao geral e comercial, consultiva e direta, com hierarquia forte nos titulos e botoes em formato pill.

## Paleta

- Primaria: azul BBB `#0b5ed7`.
- Primaria escura: `#0a4fb4`.
- Acao/destaque: laranja BBB `#f97316`.
- Destaque controlado: dourado `#f7c948`.
- Texto principal: grafite `#020617` e `#0f2143`.
- Texto secundario: `#64748b`.
- Fundo: off-white `#f8fbff`.
- Superficie: branco `#ffffff`.
- Borda: `#dbe4f0`.
- Sucesso: `#15803d`.
- Alerta: `#b45309`.
- Erro: `#b91c1c`.
- Informacao: `#0369a1`.

## Tokens

Os tokens ficam em `frontend/src/theme/bbb.ts` e tambem em variaveis CSS em `frontend/src/styles.css`.

- Raios: 8px, 12px, 16px e pill.
- Sombras: painel leve e destaque elevado.
- Campos: altura minima 44px.
- Botoes: altura minima 44px no primario e 40px no secundario.
- Tipografia: Inter com fallback seguro do sistema.
- Conteudo: largura maxima operacional `max-w-7xl`.

## Componentes

- `BrandLogo`: usa o logo oficial salvo localmente, com alternativa compacta para menu recolhido.
- `AuthShell`: base visual das telas publicas de login, recuperacao, nova senha e ativacao.
- `Layout`: menu lateral, recolhimento desktop, abertura mobile, cabecalho, perfil e logout.
- `Panel`: superficie padrao de conteudo.
- `PageHeader`: titulo operacional com assinatura BBB.
- `StatusBadge`: estados com texto e cor, sem depender somente da cor.

## Telas cobertas

- Login.
- Recuperacao de senha.
- Redefinicao de senha.
- Ativacao administrativa.
- Dashboard.
- Menu lateral e cabecalho.
- Leads e detalhe de lead.
- Clientes e consentimentos.
- Propostas.
- Simulacoes INSS e FGTS.
- Tarefas.
- WhatsApp simulado.
- Treinamentos.
- Administracao/configuracoes.

## Responsividade

O layout usa menu fixo no desktop e drawer no celular. Tabelas largas ficam dentro de area com rolagem local, sem rolagem horizontal geral. A validacao visual cobriu 390px e 1366px; os estilos usam grades responsivas para 360px, 390px, 768px, 1024px, 1366px e 1920px.

## Acessibilidade

- Foco visivel por `outline-color` e ring nos links do menu.
- Logo com texto alternativo.
- Navegacao principal com `aria-label`.
- Botoes iconicos do menu com `aria-label`.
- Contraste claro para textos, superficies, erros e avisos.
- Estados possuem texto alem de cor.

## Performance

- Imagens originais adicionadas:
  - logo JPEG: 56.52 kB.
  - banner PNG: 540.81 kB.
- Imagens otimizadas para uso preferencial:
  - logo WebP UI: 1.61 kB.
  - banner WebP desktop: 31.13 kB.
  - banner WebP mobile: 16.95 kB.
- Fallbacks locais preservados:
  - logo JPEG.
  - banner PNG.
- Build observado depois da otimizacao invisivel:
  - CSS: 21.54 kB, gzip 4.92 kB.
  - JS principal: 230.37 kB, gzip 67.63 kB.
  - Recharts isolado em chunk `vendor-charts`.
  - React/Router, formularios/validacao e icones isolados em chunks de vendor.
- `assetsInlineLimit: 0` mantem imagens como arquivos estaticos em vez de embutir assets no JavaScript.
- Nenhuma fonte remota, analytics ou rastreamento foi adicionado.

## Limites

- A referencia foi usada visualmente; nenhum HTML, CSS ou JavaScript do site oficial foi copiado.
- O frontend continua operacional, nao institucional.
- Backend, banco, migrations, endpoints, contratos, autenticacao, cookies, sessoes, permissoes, provedores, secrets e dados reais nao foram alterados.
