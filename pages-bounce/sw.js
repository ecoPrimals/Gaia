/* The old HUD's worker on Pages. Set at /hud/sw.js, scope /hud/ - it sees only what pages under /hud/ ask for.
   The old pages were written for a home where they were the root: they ask for /js/x.js, /data/y.json, /art/z.jpg.
   On Pages that root belongs to another site, so those asks miss. A 404 page never sees them (only a whole page
   landing shows it), so this is the same inference for scripts, data and pictures:
     an ask from the root   -> what the thymus has placed, then the same path under /hud/, then the root as asked
     an ask under /hud/ that misses -> what the thymus has placed, then the root
   What cannot be placed is passed on as the miss it is, and the house is asked the same path once per browser
   (the path only), where a miss becomes a stem cell for the thymus. Nothing is cached; no page is rewritten.
   Source: Gaia repo, pages-bounce/sw.js */
'use strict';
var HOME = '/hud', SITES = ['/hud/', '/nestgate.io/', '/sporePrint/'], HOUSE = 'https://primals.eco';
var LEARNED = '/hud/thymus/asks.json', LEARN_EVERY = 30 * 60 * 1000, MAX_TOLD = 8;
// a mouth with no ear: the old pages post a visitor's words here and no door, at the house or on Pages, takes them.
// The page's own word for "not kept" is heard:false, so it is told that instead of failing without a word.
var SAY = { '/mirror-message': { heard: false, why: 'no ear on this door yet' } };

var learned = null, learnedAt = 0, placed = new Map(), missed = new Map(), MISS_FOR = 5 * 60 * 1000, told = 0;

self.addEventListener('install', function () { self.skipWaiting(); });
self.addEventListener('activate', function (e) { e.waitUntil(self.clients.claim()); });

function siteOf(path) { for (var i = 0; i < SITES.length; i++) if (path.indexOf(SITES[i]) === 0) return SITES[i]; return '/'; }

function learn() {
  if (learned && Date.now() - learnedAt < LEARN_EVERY) return Promise.resolve(learned);
  return fetch(LEARNED, { cache: 'no-cache' }).then(function (r) { return r.ok ? r.json() : null; })
    .then(function (j) { learned = j || learned || {}; learnedAt = Date.now(); return learned; },
          function () { learned = learned || {}; learnedAt = Date.now(); return learned; });
}

function tellHouse(path) {
  // once per path per browser, a few per waking
  if (told >= MAX_TOLD) return;
  told++;
  caches.open('gaia-asked').then(function (c) {
    return c.match(path).then(function (hit) {
      if (hit) return;
      return fetch(HOUSE + path, { mode: 'no-cors', cache: 'no-store', credentials: 'omit', referrerPolicy: 'no-referrer' })
        .then(function () { return c.put(path, new Response('', { headers: { 'x-asked': String(Date.now()) } })); });
    });
  }).catch(function () {});
}

function elsewhere(req, url, c) { return fetch(c + url.search, { headers: req.headers, credentials: 'same-origin' }); }

function place(req, url) {
  var p = url.pathname, fromRoot = siteOf(p) === '/';
  var known = placed.get(p);
  if (known) return known === p ? fetch(req) : elsewhere(req, url, known);
  var gone = missed.get(p);
  if (gone && Date.now() - gone < MISS_FOR) return fetch(req);           // looked a moment ago: pass the miss on as it is
  // a file of the old HUD that is where it says it is: the plain way, nothing added
  var first = fromRoot ? null : fetch(req).then(function (res) { return res.status === 404 ? null : res; });
  return Promise.resolve(first).then(function (res) {
    if (res) return res;
    return learn().then(function (L) {
      var list = [], seen = {};
      function add(c) { if (c && !seen[c] && (fromRoot || c !== p)) { seen[c] = 1; list.push(c); } }
      if (L.solved && L.solved[p]) add(L.solved[p]);
      if (fromRoot) { add(HOME + p); add(p); } else { add(p.slice(HOME.length)); }
      var i = 0;
      function next() {
        if (i >= list.length) { missed.set(p, Date.now()); tellHouse(p); return fetch(req); }
        var c = list[i++];
        return (c === p ? fetch(req) : elsewhere(req, url, c)).then(function (r) {
          if (r.status === 404) return next();
          if (r.ok) placed.set(p, c);
          return r;
        }, function () { return next(); });
      }
      return next();
    });
  });
}

self.addEventListener('fetch', function (e) {
  var req = e.request, url;
  try { url = new URL(req.url); } catch (err) { return; }
  if (url.origin !== self.location.origin) return;                      // only our own origin
  if (req.method === 'POST' && SAY[url.pathname]) {
    e.respondWith(new Response(JSON.stringify(SAY[url.pathname]), { headers: { 'Content-Type': 'application/json' } }));
    return;
  }
  if (req.method !== 'GET' || req.mode === 'navigate') return;          // whole pages go the plain way: a miss lands on the bounce
  var site = siteOf(url.pathname);
  if (site !== '/' && site !== '/hud/') return;                         // another face's own file
  if (url.pathname === LEARNED || url.pathname === '/hud/sw.js') return;
  e.respondWith(place(req, url));
});
