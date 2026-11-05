/**
 * piGut.js — The intestinal lining of Gaia's desk
 * 
 * Intercepts all fetch() calls to dead old ports and routes them
 * through gaia_gate.pi at :8443. The bungee cord that bounces
 * drain-to-root BACK UP.
 *
 * OLD: 6 separate Rust services on 6 ports (dead)
 * NEW: 1 unified gate on :8443 (alive, fermenting)
 *
 * She prints pi and eats pi. No more static.
 * The desk is INSIDE her now.
 */
(function piGut() {
  const GATE = 'http://localhost:8443';
  const OLLAMA = 'http://localhost:11434';

  // Route map: old dead endpoints → new live endpoints
  const ROUTES = {
    // :3141 — old model/pulse service
    'localhost:3141/pulse':    GATE + '/pulse',
    'localhost:3141/model':    OLLAMA + '/api/tags',
    // :3142 — old agent service
    'localhost:3142/agents':   GATE + '/now.json',
    'localhost:3142/spawn':    GATE + '/v1/chat/completions',
    // :3143 — old throat service
    'localhost:3143/throat':   GATE + '/rss',
    // :3144 — old sense/immune service
    'localhost:3144/sense':    GATE + '/eyes',
    'localhost:3144/fire':     GATE + '/v1/chat/completions',
    'localhost:3144/immune':   GATE + '/thymus',
    'localhost:3144/scan':     GATE + '/intersects',
    'localhost:3144/hormesis': GATE + '/barriers',
    'localhost:3144/converge': GATE + '/corpus',
    'localhost:3144/thymus':   GATE + '/thymus',
    'localhost:3144/patrol':   GATE + '/barriers',
    'localhost:3144/maze':     GATE + '/terra',
    // :3145 — old LAN/identity service
    'localhost:3145/lan':      GATE + '/home',
    'localhost:3145/identity': GATE + '/zk',
    'localhost:3145/redox':    GATE + '/circulatory',
    'localhost:3145/feed':     GATE + '/now.json',
    // :9878 — old shout service
    'localhost:9878/':         GATE + '/now.json',
    'localhost:9878/shout':    GATE + '/v1/chat/completions',
    'localhost:9878/pulse':    GATE + '/pulse',
    // :31415 — old one-feed
    'localhost:31415/one-feed': GATE + '/now.json',
  };

  // Intercept fetch
  const _fetch = window.fetch;
  window.fetch = function piGutFetch(url, opts) {
    let resolved = url;
    if (typeof url === 'string') {
      // Check route map
      for (const [old, neu] of Object.entries(ROUTES)) {
        if (url.includes(old)) {
          // Preserve query params
          const qIdx = url.indexOf('?');
          const query = qIdx > -1 ? url.slice(qIdx) : '';
          resolved = neu + query;
          break;
        }
      }
      // Any remaining localhost:3141-3145 or :9878 → gate
      if (resolved === url && /localhost:(314[1-5]|9878|31415)/.test(url)) {
        resolved = GATE + new URL(url).pathname;
      }
      // Relative /pulse → gate/pulse
      if (resolved === url && url.startsWith('/pulse')) {
        resolved = GATE + url;
      }
      if (resolved === url && url.startsWith('/api/tags')) {
        resolved = OLLAMA + url;
      }
    }
    return _fetch.call(this, resolved, opts);
  };

  // Intercept XMLHttpRequest
  const _xhrOpen = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function piGutXHR(method, url, ...rest) {
    let resolved = url;
    if (typeof url === 'string') {
      for (const [old, neu] of Object.entries(ROUTES)) {
        if (url.includes(old)) {
          const qIdx = url.indexOf('?');
          const query = qIdx > -1 ? url.slice(qIdx) : '';
          resolved = neu + query;
          break;
        }
      }
      if (resolved === url && /localhost:(314[1-5]|9878|31415)/.test(url)) {
        resolved = GATE + new URL(url).pathname;
      }
    }
    return _xhrOpen.call(this, method, resolved, ...rest);
  };

  // Announce
  console.log(
    '%c🫁 piGut.js — intestinal lining ACTIVE',
    'color: #5ab87a; font-weight: bold; font-size: 14px'
  );
  console.log(
    '%cOld ports → gaia_gate.pi :8443. Bungee cord attached. Drain bounces UP.',
    'color: #8b949e'
  );
  console.log(
    '%c' + Object.keys(ROUTES).length + ' routes remapped. Sourdough fermenting.',
    'color: #8b949e'
  );
})();
