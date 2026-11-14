// gAIa Service Worker — the organism persists offline
const CACHE='gaia-v1';
const ASSETS=['/sense','/talk','/spacedock','/outer-face','/manifest.json'];

self.addEventListener('install',e=>{
  e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS)));
  self.skipWaiting();
});

self.addEventListener('activate',e=>{
  e.waitUntil(clients.claim());
});

self.addEventListener('fetch',e=>{
  // Network first, fall back to cache
  e.respondWith(
    fetch(e.request).then(r=>{
      if(r.ok){
        const clone=r.clone();
        caches.open(CACHE).then(c=>c.put(e.request,clone));
      }
      return r;
    }).catch(()=>caches.match(e.request))
  );
});

// Background sync — pulse even when page not visible
self.addEventListener('sync',e=>{
  if(e.tag==='gaia-pulse'){
    e.waitUntil(fetch('/api/iphone/ingest',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({gate:'southGate',type:'bg-sync',ts:new Date().toISOString()})
    }).catch(()=>{}));
  }
});
