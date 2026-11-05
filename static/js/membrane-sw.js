// membrane-sw.js — service worker for cellular resilience
// v2: Fixed cache-first trapping. HTML is now network-first so version bumps propagate.
// Caches surfaces on WiFi, serves from cache when towers block.
// Reports connectivity status back to the relay.
// The membrane extends to every device that touches it.
//
var CACHE_NAME = 'membrane-v10-4';

// Live feeds — network-first, cache fallback
var FEEDS = [
  'dashboard.json', 'human.json', 'braid.json', 'topology.json',
  'chipmunk.json', 'presence.json', 'tower.json', 'billboard',
  'scan_sweep_sort.json', 'negentropy.json', 'touches.json',
  'totality.json', 'subgraphs.json', 'seo.json', 'pi-ranges.json',
  'signal/pulse',
  'dialogue.json',
];

self.addEventListener('install', function(e) {
  // Skip waiting — activate immediately so new version takes over
  self.skipWaiting();
});

self.addEventListener('activate', function(e) {
  // Clear ALL old caches — nuclear cleanup
  e.waitUntil(
    caches.keys().then(function(names) {
      return Promise.all(
        names.filter(function(n) { return n !== CACHE_NAME; })
             .map(function(n) { return caches.delete(n); })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', function(e) {
  var url = new URL(e.request.url);

  // Only handle same-origin requests
  if (url.origin !== self.location.origin) return;

  // Signal relay — always pass through to network
  if (url.pathname.indexOf('/signal/') >= 0) return;
  if (url.pathname.indexOf('/chipmunk/note') >= 0) return;

  // POST requests — always network
  if (e.request.method !== 'GET') return;

  // HTML pages (index.html, /, /desk/) — NETWORK FIRST always
  // This is the critical fix: HTML must always be fresh so new script versions load
  var isHTML = e.request.headers.get('accept') && e.request.headers.get('accept').indexOf('text/html') >= 0;
  var isRoot = url.pathname === '/' || url.pathname.endsWith('.html') || url.pathname.endsWith('/');
  if (isHTML || isRoot) {
    e.respondWith(networkFirstThenCache(e.request));
    return;
  }

  // Live feeds — network first, cache fallback
  var isFeed = FEEDS.some(function(f) { return url.pathname.indexOf(f) >= 0; });
  if (isFeed) {
    e.respondWith(networkFirstThenCache(e.request));
    return;
  }

  // JS/CSS with version params (?v=53) — cache first is safe because
  // the version param makes each version a unique URL
  var hasVersion = url.search.indexOf('v=') >= 0;
  if (hasVersion) {
    e.respondWith(cacheFirstThenNetwork(e.request));
    return;
  }

  // Static assets without version params — network first to stay fresh
  e.respondWith(networkFirstThenCache(e.request));
});

function networkFirstThenCache(request) {
  return fetch(request).then(function(response) {
    if (response.ok) {
      var clone = response.clone();
      caches.open(CACHE_NAME).then(function(cache) {
        cache.put(request, clone);
      });
    }
    return response;
  }).catch(function() {
    return caches.match(request).then(function(cached) {
      if (cached) return cached;
      // Return empty JSON if nothing cached and it looks like a feed
      if (request.url.indexOf('.json') >= 0) {
        return new Response('{"offline":true,"cached":false}', {
          headers: { 'Content-Type': 'application/json' }
        });
      }
      return new Response('', { status: 503 });
    });
  });
}

function cacheFirstThenNetwork(request) {
  return caches.match(request).then(function(cached) {
    if (cached) return cached;
    return fetch(request).then(function(response) {
      if (response.ok) {
        var clone = response.clone();
        caches.open(CACHE_NAME).then(function(cache) {
          cache.put(request, clone);
        });
      }
      return response;
    }).catch(function() {
      return new Response('', { status: 503 });
    });
  });
}

// ═══ CONNECTIVITY PROBE ═══
var SURFACES = [
  'https://tuebor.primals.eco/',
  'https://clutch.primals.eco/',
  'https://detroit.primals.eco/',
  'https://hud.primals.eco/',
  'https://sporeprint.primals.eco/',
  'https://gorilla.primals.eco/',
  'https://hypothesis.primals.eco/',
  'https://barry.primals.eco/',
];

var _probeTimer = null;

function probeSurfaces() {
  var results = {};
  var promises = SURFACES.map(function(url) {
    var start = Date.now();
    return fetch(url, { method: 'HEAD', mode: 'no-cors', cache: 'no-store' })
      .then(function() {
        results[url] = { reachable: true, latency: Date.now() - start };
      })
      .catch(function() {
        results[url] = { reachable: false, latency: -1 };
      });
  });

  Promise.all(promises).then(function() {
    var conn = navigator.connection || {};
    var netInfo = {
      type: conn.type || 'unknown',
      effectiveType: conn.effectiveType || '?',
      downlink: conn.downlink || 0,
      rtt: conn.rtt || 0,
    };

    self.clients.matchAll().then(function(clients) {
      clients.forEach(function(client) {
        client.postMessage({
          type: 'membrane-probe',
          surfaces: results,
          network: netInfo,
          timestamp: Date.now(),
        });
      });
    });
  });
}

self.addEventListener('message', function(e) {
  if (e.data === 'start-probe') {
    if (!_probeTimer) {
      probeSurfaces();
      _probeTimer = setInterval(probeSurfaces, 60000);
    }
  }
  if (e.data === 'stop-probe') {
    if (_probeTimer) { clearInterval(_probeTimer); _probeTimer = null; }
  }
  // Force cache clear on demand
  if (e.data === 'clear-cache') {
    caches.keys().then(function(names) {
      names.forEach(function(n) { caches.delete(n); });
    });
  }
});
