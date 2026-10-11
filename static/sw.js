/**
 * Oman Geospatial Platform - Client-Side Cache Service Worker
 * Provides instant 0ms offline tile caching for buttery-smooth panning and zooming.
 */
const CACHE_NAME = 'oman-map-v1';

// URL patterns to cache automatically
const CACHE_MATCH_PATTERNS = [
  '/api/tiles/',
  '/api/network/edges/tile/',
  '/api/boundaries',
  '/api/mask',
  '/api/terrain',
  '/api/network/stats',
  '/api/network/features'
];

self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const url = event.request.url;
  const shouldCache = CACHE_MATCH_PATTERNS.some((pattern) => url.includes(pattern));

  if (!shouldCache || event.request.method !== 'GET') {
    return;
  }

  // Cache-First with Stale-While-Revalidate fallback
  event.respondWith(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.match(event.request).then((cachedResponse) => {
        if (cachedResponse) {
          return cachedResponse;
        }

        // Fetch from network and save clone in cache
        return fetch(event.request).then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            cache.put(event.request, networkResponse.clone());
          }
          return networkResponse;
        }).catch(() => {
          // If offline and request fails
          return new Response('', { status: 408, statusText: 'Request timed out / offline' });
        });
      });
    })
  );
});

// Support messages from page to manage cache
self.addEventListener('message', (event) => {
  if (event.data && event.data.action === 'CLEAR_CACHE') {
    caches.delete(CACHE_NAME).then(() => {
      if (event.ports && event.ports[0]) {
        event.ports[0].postMessage({ status: 'CLEARED' });
      }
    });
  } else if (event.data && event.data.action === 'GET_STATS') {
    caches.open(CACHE_NAME).then((cache) => {
      cache.keys().then((keys) => {
        if (event.ports && event.ports[0]) {
          event.ports[0].postMessage({ count: keys.length });
        }
      });
    });
  }
});
