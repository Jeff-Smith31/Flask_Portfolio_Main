/* Simple service worker for offline support */
const CACHE_NAME = 'portfolio-cache-v1';
const OFFLINE_URL = '/offline';
const CORE_ASSETS = [
  '/',
  '/work',
  '/services',
  '/about',
  '/contact',
  '/resume',
  OFFLINE_URL,
  '/static/css/style.css',
  '/static/js/main.js',
  '/static/manifest.webmanifest',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(CORE_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(
      keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k))
    ))
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  const url = new URL(req.url);

  // Only handle same-origin requests
  if (url.origin !== self.location.origin) return;

  // For navigation requests, try network first, then cache, then offline page
  if (req.mode === 'navigate') {
    event.respondWith(
      fetch(req)
        .then((res) => {
          const resClone = res.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(req, resClone)).catch(() => {});
          return res;
        })
        .catch(async () => {
          const cache = await caches.open(CACHE_NAME);
          const cached = await cache.match(req);
          return cached || cache.match(OFFLINE_URL);
        })
    );
    return;
  }

  // For other requests, use cache-first then network
  event.respondWith(
    caches.match(req).then((cached) => {
      if (cached) return cached;
      return fetch(req).then((res) => {
        const resClone = res.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(req, resClone)).catch(() => {});
        return res;
      }).catch(() => caches.match(OFFLINE_URL));
    })
  );
});
