# Deploy Controlado do Frontend na Vercel

Este guia publica o frontend React/Vite do BBB Consig CRM em ambiente de teste controlado.

## Configuracao do projeto
- Root directory: `frontend`
- Build command: `npm run build`
- Output directory: `dist`
- Framework: Vite

## Variavel obrigatoria
- `VITE_API_URL`: URL publica do backend, exemplo `https://seu-backend.onrender.com`.

## SPA fallback
O arquivo `frontend/vercel.json` adiciona rewrite para `index.html`, permitindo rotas como `/dashboard`, `/leads` e `/login` com React Router.

## Passo a passo
1. Criar projeto Vercel apontando para a pasta `frontend`.
2. Definir `VITE_API_URL` no painel da Vercel.
3. Rodar deploy.
4. Abrir `/login`.
5. Entrar com usuario demo.
6. Validar `/dashboard`, `/leads`, `/clientes`, `/propostas` e `/whatsapp`.

## Cuidados
Este deploy e controlado/teste. Nao usar dados reais antes de validar seguranca, dominios, CORS, HTTPS, politicas de acesso e armazenamento definitivo. WhatsApp, INSS, FGTS e bancos seguem simulados.
