// Service worker: deixa o app abrir offline e pega versões novas quando tem internet.
const CACHE = 'manual-v5';
const SHELL = ['./', './index.html', './manifest.webmanifest', './icons/icon-192.png', './icons/apple-touch-icon.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);

  // Tráfego do Firebase (login e banco) nunca passa pelo cache.
  if (/googleapis\.com|firebaseapp\.com|google\.com$/.test(url.hostname) && !url.pathname.startsWith('/css')) return;

  // Página e arquivos do app: tenta a rede primeiro (pra receber atualizações), cai no cache se estiver offline.
  if (url.origin === self.location.origin) {
    e.respondWith(
      fetch(req)
        .then(res => { const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); return res; })
        .catch(() => caches.match(req).then(r => r || caches.match('./index.html')))
    );
    return;
  }

  // Bibliotecas e fontes (gstatic, Google Fonts): cache primeiro.
  if (/gstatic\.com|fonts\.googleapis\.com/.test(url.hostname)) {
    e.respondWith(
      caches.match(req).then(hit => hit || fetch(req).then(res => {
        const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); return res;
      }))
    );
  }
});
