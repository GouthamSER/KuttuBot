/* KuttuBot service worker: makes the site installable and shows a friendly page when offline.
   Network first for pages, never caches /api (search results must stay live). */
const CACHE = "kuttu-v1";
const SHELL = ["/", "/manifest.webmanifest", "/icons/icon-192.png", "/icons/icon-512.png"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).catch(() => {}));
  self.skipWaiting();
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  const url = new URL(req.url);
  if (req.method !== "GET" || url.origin !== location.origin || url.pathname.startsWith("/api/")) return;

  if (req.mode === "navigate") {                       // page: network first, cached shell when offline
    e.respondWith(
      fetch(req).then((res) => {
        if (url.pathname === "/") { const copy = res.clone(); caches.open(CACHE).then((c) => c.put("/", copy)); }
        return res;
      }).catch(() => caches.match("/").then((r) => r || new Response(
        "<meta name=viewport content='width=device-width'><body style='background:#0b0b10;color:#eee;font:16px sans-serif;text-align:center;padding-top:40vh'>You are offline. Check your internet and reopen KuttuBot.",
        { headers: { "Content-Type": "text/html" } })))
    );
    return;
  }
  if (url.pathname.startsWith("/icons/") || url.pathname === "/manifest.webmanifest") {   // static: cache first
    e.respondWith(caches.match(req).then((r) => r || fetch(req)));
  }
});
