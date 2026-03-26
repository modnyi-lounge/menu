const CACHE_NAME = 'modnyi-v2'; // Менять версию при глобальных правках стилей

// 1. Файлы, которые нужны для работы оболочки (Shell)
const STATIC_ASSETS = [
  './',
  './manifest.json',
  './sw.js',
  './assets/logo.svg',
  './assets/icon-192x192.png',
  './assets/icon-512x512.png'
];

// Установка: кэшируем статику
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

// Активация: чистим старые кэши
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(
      keys.map((key) => {
        if (key !== CACHE_NAME) return caches.delete(key);
      })
    ))
  );
});

// 2. Стратегия перехвата запросов
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // СТРАТЕГИЯ ДЛЯ HTML (Network First)
  if (event.request.mode === 'navigate') {
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          // Если сеть есть, сохраняем свежий HTML в кэш
          const copy = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
          return response;
        })
        .catch(() => {
          // Если сети нет, отдаем из кэша
          return caches.match(event.request);
        })
    );
    return;
  }

  // СТРАТЕГИЯ ДЛЯ КАРТИНОК И РЕСУРСОВ (Cache First, but update)
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse; // Мгновенно отдаем из кэша
      }
      return fetch(event.request).then((networkResponse) => {
          // Сохраняем ТОЛЬКО если статус 200 (OK)
          if (networkResponse.status === 200) {
              const responseClone = networkResponse.clone();
              caches.open(CACHE_NAME).then((cache) => cache.put(event.request, responseClone));
          }
          return networkResponse;
      })
      .catch(() => {
          // Возвращаем пустой ответ со статусом 204 (No Content)
          // Это легальный "успешный" статус, который не красит консоль в красный
          return new Response(null, { status: 204 }); 
      });
    })
  );
});
