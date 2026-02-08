/**
 * Service Worker v10 for Ahoy Indie Media
 * Provides offline caching with smart strategies per request type.
 *
 * Strategies:
 *   HTML (navigate)        → network-first, cache fallback
 *   Versioned static assets → cache-first (version in URL prevents staleness)
 *   Cacheable API endpoints → stale-while-revalidate
 *   Audio/video/streams    → skip (too large)
 *   /refresh               → skip (escape hatch)
 */

const CACHE_VERSION = 'v10';
const SHELL_CACHE = `ahoy-shell-${CACHE_VERSION}`;
const STATIC_CACHE = `ahoy-static-${CACHE_VERSION}`;
const API_CACHE = `ahoy-api-${CACHE_VERSION}`;
const ALL_CACHES = [SHELL_CACHE, STATIC_CACHE, API_CACHE];

// Only pre-cache the offline fallback and essential icons.
// Versioned CSS/JS will cache on first use (their URLs contain ?v= query params).
const PRECACHE_URLS = [
    '/offline',
    '/static/images/icon-192.png',
    '/static/images/icon-512.png',
    '/static/img/default-cover.jpg',
    '/static/img/ahoy_logo.png'
];

// API endpoints safe to cache (read-only, public data)
const CACHEABLE_API = new Set([
    '/api/music',
    '/api/shows',
    '/api/artists',
    '/api/whats-new',
    '/api/live-tv/channels'
]);

// ── Install ──────────────────────────────────────────────────────────
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(SHELL_CACHE)
            .then((cache) => cache.addAll(PRECACHE_URLS))
            .then(() => self.skipWaiting())
    );
});

// ── Activate ─────────────────────────────────────────────────────────
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys()
            .then((names) => Promise.all(
                names.map((name) => {
                    if (!ALL_CACHES.includes(name)) {
                        return caches.delete(name);
                    }
                })
            ))
            .then(() => self.clients.claim())
    );
});

// ── Fetch ────────────────────────────────────────────────────────────
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip non-GET
    if (request.method !== 'GET') return;

    // Skip media files (too large to cache)
    if (/\.(mp3|mp4|wav|m4a|ogg|webm|m3u8|ts)(\?|$)/i.test(url.pathname) ||
        url.pathname.startsWith('/stream')) return;

    // Skip the /refresh escape hatch (must always hit network)
    if (url.pathname === '/refresh') return;

    // ── API routes ──
    if (url.pathname.startsWith('/api/')) {
        if (!CACHEABLE_API.has(url.pathname)) return; // non-cacheable API: network only

        event.respondWith(staleWhileRevalidate(request, API_CACHE));
        return;
    }

    // ── HTML navigation ──
    if (request.mode === 'navigate' || request.destination === 'document') {
        event.respondWith(networkFirstHTML(request));
        return;
    }

    // ── Static assets under /static/ ──
    if (url.pathname.startsWith('/static/')) {
        event.respondWith(cacheFirst(request, STATIC_CACHE));
        return;
    }

    // ── Everything else (CDN scripts, fonts, etc.) ──
    event.respondWith(networkFirstGeneric(request, STATIC_CACHE));
});

// ── Message handler ──────────────────────────────────────────────────
self.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    if (event.data && event.data.type === 'CLEAR_CACHES') {
        caches.keys().then((names) => {
            names.forEach((name) => caches.delete(name));
        });
    }
});

// ── Strategies ───────────────────────────────────────────────────────

/**
 * Network-first for HTML pages.
 * Always try the network (with cache: 'no-store' to skip browser HTTP cache).
 * On success, cache the response in SHELL_CACHE.
 * On failure, serve from cache. If nothing cached, serve /offline.
 */
async function networkFirstHTML(request) {
    try {
        const response = await fetch(request, { cache: 'no-store' });
        if (response && response.status === 200) {
            const cache = await caches.open(SHELL_CACHE);
            cache.put(request, response.clone());
        }
        return response;
    } catch (e) {
        const cached = await caches.match(request);
        if (cached) return cached;
        return caches.match('/offline');
    }
}

/**
 * Cache-first for versioned static assets.
 * Since CSS/JS URLs contain ?v=xxx, a new version is a new cache key.
 * Old entries are never served; they get cleaned up on SW version bump.
 */
async function cacheFirst(request, cacheName) {
    const cached = await caches.match(request);
    if (cached) return cached;

    try {
        const response = await fetch(request);
        if (response && response.status === 200) {
            const cache = await caches.open(cacheName);
            cache.put(request, response.clone());
        }
        return response;
    } catch (e) {
        return new Response('', { status: 408 });
    }
}

/**
 * Stale-while-revalidate for API endpoints.
 * Serve cached immediately if available, update cache in background.
 * If no cache and network fails, return a JSON offline error.
 */
async function staleWhileRevalidate(request, cacheName) {
    const cache = await caches.open(cacheName);
    const cached = await cache.match(request);

    const networkFetch = fetch(request)
        .then((response) => {
            if (response && response.status === 200) {
                cache.put(request, response.clone());
            }
            return response;
        })
        .catch(() => null);

    if (cached) {
        // Serve stale, update in background
        networkFetch.catch(() => {});
        return cached;
    }

    // No cache — wait for network
    const response = await networkFetch;
    if (response) return response;

    // Network failed, no cache — return offline JSON
    return new Response(
        JSON.stringify({ error: 'offline', offline: true }),
        { status: 503, headers: { 'Content-Type': 'application/json' } }
    );
}

/**
 * Network-first for generic resources (CDN scripts, fonts, etc.).
 * Try network, cache on success, fall back to cache.
 */
async function networkFirstGeneric(request, cacheName) {
    try {
        const response = await fetch(request);
        if (response && response.status === 200) {
            const cache = await caches.open(cacheName);
            cache.put(request, response.clone());
        }
        return response;
    } catch (e) {
        const cached = await caches.match(request);
        if (cached) return cached;
        return new Response('', { status: 408 });
    }
}
