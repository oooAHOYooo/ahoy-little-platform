/**
 * Service Worker for Ahoy Indie Media
 * Provides offline caching for UI shell and static assets
 */

const CACHE_NAME = 'ahoy-indie-media-v7';
const STATIC_CACHE_URLS = [
    '/',
    '/static/css/loader.css',
    '/static/css/main.css',
    '/static/css/base.css',
    '/static/css/global.css',
    '/static/css/mobile.css',
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
    
    event.respondWith(
        caches.match(request)
            .then((cachedResponse) => {
                if (cachedResponse) {
                    console.log('Service Worker: Serving from cache', request.url);
                    return cachedResponse;
                }
                
                console.log('Service Worker: Fetching from network', request.url);
                return fetch(request)
                    .then((response) => {
                        // Don't cache non-successful responses
                        if (!response || response.status !== 200 || response.type !== 'basic') {
                            return response;
                        }
                        
                        // Clone the response for caching
                        const responseToCache = response.clone();
                        
                        caches.open(CACHE_NAME)
                            .then((cache) => {
                                cache.put(request, responseToCache);
                            });
                        
                        return response;
                    })
                    .catch((error) => {
                        console.error('Service Worker: Fetch failed', error);
                        
                        // Return offline page for navigation requests
                        if (request.mode === 'navigate') {
                            return caches.match('/');
                        }
                        
                        throw error;
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
