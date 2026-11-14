var CACHE = "membrane-v1";
var PRECACHE = ["/identity", "/manifest.json"];

self.addEventListener("install", function(e) {
  e.waitUntil(caches.open(CACHE).then(function(c) { return c.addAll(PRECACHE) }));
  self.skipWaiting();
});

self.addEventListener("fetch", function(e) {
  e.respondWith(
    fetch(e.request).catch(function() {
      return caches.match(e.request);
    })
  );
});
