/* TraderVikingBR · Live Desk — Service Worker
   Estrategia:
   - App shell (HTML, manifest, icones): stale-while-revalidate
   - Bibliotecas do CDN: cache-first (versionadas, nao mudam)
   - Pacotes de dados (dados/*.json): network-first com fallback para cache
*/
const VERSION = 'tvbr-v1';
const SHELL = VERSION + '-shell';
const LIBS  = VERSION + '-libs';
const DATA  = VERSION + '-data';

const SHELL_FILES = [
  './',
  './index.html',
  './manifest.webmanifest',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-maskable-512.png'
];

const LIB_FILES = [
  'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js',
  'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js',
  'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js',
  'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js'
];

self.addEventListener('install', e => {
  e.waitUntil((async () => {
    const shell = await caches.open(SHELL);
    await shell.addAll(SHELL_FILES).catch(() => {});
    const libs = await caches.open(LIBS);
    await Promise.all(LIB_FILES.map(u =>
      fetch(u, { mode: 'cors' }).then(r => r.ok && libs.put(u, r)).catch(() => {})
    ));
    self.skipWaiting();
  })());
});

self.addEventListener('activate', e => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter(k => !k.startsWith(VERSION)).map(k => caches.delete(k)));
    await self.clients.claim();
  })());
});

self.addEventListener('message', e => {
  if (e.data === 'skipWaiting') self.skipWaiting();
  if (e.data === 'clearData') caches.delete(DATA);
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);

  // Pacotes de dados publicados pelo publicar_radar.py
  if (url.pathname.includes('/dados/') && url.pathname.endsWith('.json')) {
    e.respondWith((async () => {
      const cache = await caches.open(DATA);
      try {
        const fresh = await fetch(req, { cache: 'no-store' });
        if (fresh && fresh.ok) cache.put(req, fresh.clone());
        return fresh;
      } catch (err) {
        const hit = await cache.match(req, { ignoreSearch: true });
        if (hit) return hit;
        return new Response(JSON.stringify({ offline: true, datas: [], partidas: [] }), {
          status: 200, headers: { 'Content-Type': 'application/json' }
        });
      }
    })());
    return;
  }

  // Bibliotecas externas
  if (url.origin !== location.origin) {
    e.respondWith((async () => {
      const cache = await caches.open(LIBS);
      const hit = await cache.match(req);
      if (hit) return hit;
      try {
        const res = await fetch(req);
        if (res && res.ok) cache.put(req, res.clone());
        return res;
      } catch (err) {
        return hit || Response.error();
      }
    })());
    return;
  }

  // App shell
  e.respondWith((async () => {
    const cache = await caches.open(SHELL);
    const hit = await cache.match(req, { ignoreSearch: true });
    const net = fetch(req).then(res => {
      if (res && res.ok) cache.put(req, res.clone());
      return res;
    }).catch(() => null);
    if (hit) { net; return hit; }
    const res = await net;
    if (res) return res;
    return (await cache.match('./index.html')) || Response.error();
  })());
});
