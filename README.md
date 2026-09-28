# Manual de Ser Humano

App pessoal de hábitos, agenda e metas, organizado em 4 pilares: saúde, namorado, filho e organização.

- **Site**: https://posroot766.github.io/manual-de-ser-humano/
- **Dados**: Firebase Firestore (projeto `manual-de-ser-humano`), acesso travado por login Google a um único e-mail
- **Instalação**: abrir o site no Safari → Compartilhar → Adicionar à Tela de Início

## Arquivos

- `index.html`: o app inteiro (HTML, CSS e JS)
- `sw.js`: service worker (offline e atualizações)
- `manifest.webmanifest` e `icons/`: instalação como app

## Backup

Tela **Sucesso** → **Baixar backup** gera um JSON com todos os dados. **Importar backup** restaura a partir desse arquivo.
Os dados pessoais nunca ficam neste repositório.

## Atualizar

Ao mudar `index.html`, suba o número em `CACHE` no `sw.js` pra forçar a atualização nos aparelhos.

## Caixa de entrada (Claude → agenda)

O Claude adiciona compromissos com `tools/inbox.py`, que grava mensagens criptografadas em `inbox.json`.
O app descriptografa com a chave privada guardada no Firebase (`meta/claudekey`) e aplica na agenda ao abrir.
A chave pública fica em `tools/claude_pubkey.txt` (Sucesso → Conexão com o Claude → Copiar código).
