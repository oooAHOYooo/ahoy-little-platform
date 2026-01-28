/**
 * Service Worker for Ahoy Indie Media
 * Provides offline caching for UI shell and static assets
 */

const CACHE_NAME = 'ahoy-indie-media-v9';
const STATIC_CACHE_URLS = [
    '/',
    '/static/css/loader.css',
    '/static/css/main.css',
    '/static/css/combined.css',
    '/static/css/design-tokens.css',
    '/static/js/loader.js',
    '/static/js/app.js',
    '/static/js/player.js',
    '/static/js/bookmarks.js',
    '/static/js/guest-bootstrap.js',
    '/static/images/icon-192.png',
    '/static/images/icon-512.png',
    '/static/img/default-cover.jpg',
    '/static/img/ahoy_logo.png'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
    console.log('Service Worker: Installing...');
    
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('Service Worker: Caching static assets');
                return cache.addAll(STATIC_CACHE_URLS);
            })
            .then(() => {
                console.log('Service Worker: Installation complete');
                return self.skipWaiting();
            })
            .catch((error) => {
                console.error('Service Worker: Installation failed', error);
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('Service Worker: Activating...');
    
    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames.map((cacheName) => {
                        if (cacheName !== CACHE_NAME) {
                            console.log('Service Worker: Deleting old cache', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('Service Worker: Activation complete');
                return self.clients.claim();
            })
    );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }
    
    // Skip audio/video streams (don't cache)
    if (request.url.includes('.mp3') || request.url.includes('.mp4') || request.url.includes('.wav')) {
        return;
    }
    
    // Cache a small set of "static" API endpoints with stale-while-revalidate
    // (improves speed without losing features, because we still revalidate)
    const cacheableApi = new Set([
        '/api/music',
        '/api/shows',
        '/api/artists',
        '/api/live-tv/channels'
    ]);

    if (url.pathname.startsWith('/api/')) {
        if (!cacheableApi.has(url.pathname)) {
            // Other API calls: always fetch fresh
            return;
        }

        event.respondWith((async () => {
            const cache = await caches.open(CACHE_NAME);
            const cached = await cache.match(request);

            const networkFetch = fetch(request)
                .then((response) => {
                    if (response && response.status === 200) {
                        cache.put(request, response.clone());
                    }
                    return response;
                })
                .catch(() => null);

            // Serve cached immediately if present, update in background
            if (cached) {
                networkFetch.catch(() => {});
                return cached;
            }

            // Otherwise wait for network
            const net = await networkFetch;
            return net || cached;
        })());
        return;
    }
    
    // HTML pages and navigation: Network-first (ensures users see latest push)
    // Static assets (images, fonts): Cache-first (faster loading)
    const isNavigationOrHTML = request.mode === 'navigate' ||
        request.destination === 'document' ||
        url.pathname === '/' ||
        url.pathname.endsWith('.html');

    const isStaticAsset = url.pathname.startsWith('/static/images/') ||
        url.pathname.startsWith('/static/img/') ||
        url.pathname.startsWith('/static/fonts/') ||
        url.pathname.endsWith('.png') ||
        url.pathname.endsWith('.jpg') ||
        url.pathname.endsWith('.jpeg') ||
        url.pathname.endsWith('.gif') ||
        url.pathname.endsWith('.webp') ||
        url.pathname.endsWith('.ico') ||
        url.pathname.endsWith('.woff') ||
        url.pathname.endsWith('.woff2');

    if (isNavigationOrHTML) {
        // Network-first for HTML pages - ensures users always see latest content
        event.respondWith(
            fetch(request)
                .then((response) => {
                    if (response && response.status === 200) {
                        const responseToCache = response.clone();
                        caches.open(CACHE_NAME).then((cache) => {
                            cache.put(request, responseToCache);
                        });
                    }
                    return response;
                })
                .catch(() => {
                    // Offline fallback
                    return caches.match(request).then((cached) => cached || caches.match('/'));
                })
        );
        return;
    }

    if (isStaticAsset) {
        // Cache-first for images/fonts (they don't change often)
        event.respondWith(
            caches.match(request).then((cachedResponse) => {
                if (cachedResponse) {
                    return cachedResponse;
                }
                return fetch(request).then((response) => {
                    if (response && response.status === 200 && response.type === 'basic') {
                        const responseToCache = response.clone();
                        caches.open(CACHE_NAME).then((cache) => {
                            cache.put(request, responseToCache);
                        });
                    }
                    return response;
                });
            })
        );
        return;
    }

    // Stale-while-revalidate for CSS/JS (fast load + background update)
    event.respondWith(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.match(request).then((cachedResponse) => {
                const fetchPromise = fetch(request).then((networkResponse) => {
                    if (networkResponse && networkResponse.status === 200 && networkResponse.type === 'basic') {
                        cache.put(request, networkResponse.clone());
                    }
                    return networkResponse;
                }).catch(() => cachedResponse);

                // Return cached immediately, update in background
                return cachedResponse || fetchPromise;
            });
        })
    );
});

// Background sync for offline actions (future enhancement)
self.addEventListener('sync', (event) => {
    console.log('Service Worker: Background sync', event.tag);
    
    if (event.tag === 'background-sync') {
        event.waitUntil(
            // Future: sync offline actions when back online
            Promise.resolve()
        );
    }
});

// Push notifications (future enhancement)
self.addEventListener('push', (event) => {
    console.log('Service Worker: Push notification received');
    
    const options = {
        body: event.data ? event.data.text() : 'New content available',
        icon: '/static/images/icon-192.png',
        badge: '/static/images/icon-192.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'explore',
                title: 'Explore',
                icon: '/static/images/icon-192.png'
            },
            {
                action: 'close',
                title: 'Close',
                icon: '/static/images/icon-192.png'
            }
        ]
    };
    
    event.waitUntil(
        self.registration.showNotification('Ahoy Indie Media', options)
    );
});
