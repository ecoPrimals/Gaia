/* hud-widget.js — HUD widget panel system.
 * Manages the grid of info panels (circulatory, desk, core, neutron, etc).
 * Reads data-cns-* attributes for context-aware panel display. */
(function(){
  "use strict";
  var widgets = {};
  function register(id, render) { widgets[id] = render; }
  function renderAll() { for (var id in widgets) { try { widgets[id](); } catch(e) { console.warn("widget " + id + ":", e.message); } } }
  function count() { return Object.keys(widgets).length; }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", function(){ setTimeout(renderAll, 1000); });
  else setTimeout(renderAll, 1000);
  window.HudWidget = { register: register, renderAll: renderAll, count: count };
})();
