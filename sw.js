/* Service worker: offline support for the CloudOps notes PWA.
   - Page (navigation / index.html): network-first, so edits show up as soon as you're online;
     falls back to the cached copy when offline.
   - Static assets (icons, manifest): cache-first.
   Bump CACHE only when the list of PRECACHE files changes. */
const CACHE = 'cloudops-v2';
const PRECACHE = [
  './',
  './index.html',
  './manifest.webmanifest',
  './icons/icon.svg',
  './icons/apple-touch-icon.png',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-maskable-512.png',
  './icons/favicon-32.png'
];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(PRECACHE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  const url = new URL(req.url);
  if (req.method !== 'GET' || url.origin !== self.location.origin) return;

  // The app page: the scope root ("./") or "./index.html" (query/hash ignored).
  const scopePath = new URL(self.registration.scope).pathname;
  const isAppPage = url.pathname === scopePath || url.pathname === scopePath + 'index.html';

  if (req.mode === 'navigate' || isAppPage) {
    e.respondWith(
      fetch(req)
        .then((res) => {
          // Only a successful response for the real app page may replace the offline copy
          // (never cache a 404 / error page as index.html).
          if (res.ok && isAppPage) {
            const copy = res.clone();
            caches.open(CACHE).then((c) => c.put('./index.html', copy));
          }
          return res;
        })
        .catch(() => (isAppPage
          ? caches.match('./index.html').then((r) => r || caches.match('./'))
          : caches.match(req).then((r) => r || caches.match('./index.html'))))
    );
    return;
  }

  e.respondWith(
    caches.match(req).then((hit) => hit || fetch(req).then((res) => {
      if (res.ok) { const copy = res.clone(); caches.open(CACHE).then((c) => c.put(req, copy)); }
      return res;
    }))
  );
});
