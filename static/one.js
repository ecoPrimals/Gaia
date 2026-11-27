/* one.js - the one state every face of the HUD keeps between them on this device.

   The HUD is one system with several faces: the HUD's own page, the atlas (whole, and as the clock face on the HUD's
   centre), the house drawn as a world. Each is a page of its own and can be opened alone. What makes them one is
   this: they hold the same clock and stand on the same place, and when one of them changes either, the others follow.

     gaiaOne.state.ahead    how far the clock stands from the real one, in milliseconds (0 = now)
     gaiaOne.state.place    the pin stood on: {id, name, lat, lon} - or null, which every face reads as home
     gaiaOne.set({ahead: ms})  /  gaiaOne.set({place: pin})     change it here and tell the other faces
     gaiaOne.on(function (state, changed, heard) { ... })       be told when it changes; heard = another face did it
     gaiaOne.hush(true)                                          keep changes to this face for a while (a clock run fast)

   The faces talk over a BroadcastChannel, which reaches only pages of this site open in this browser. Nothing of
   it is sent anywhere, and nothing is stored. A place is always a pin of the atlas - a public building or a town.
   Where a visitor stands is never put here.

   The shared pieces every face reads, each the one place its subject is worked out:
     /static/sky.js          the sun, the moon, the fixed stars, the calendar
     /static/house.js        the gates of the house, how each stands in the mesh, the engine's picture of them
     /static/atlas-pins.json the ground: the pins, the triangle, the spore graph, the moments
     /static/one.js          this: the clock and the place */
(function (root) {
  'use strict';
  var me = Math.random().toString(36).slice(2), chan = null, hushed = false, wait = 0, heard = [], pending = {};
  var state = {ahead: 0, place: null};
  function same(a, b) { return a === b || (!!a && !!b && a.id === b.id); }
  function clean(p) {                                                 // a place is four plain things, nothing more
    if (!p || typeof p.id !== 'string' || !/^[\w-]{1,64}$/.test(p.id) || !isFinite(p.lat) || !isFinite(p.lon)) return null;
    return {id: p.id, name: String(p.name || p.id).slice(0, 120), lat: +p.lat, lon: +p.lon};
  }
  function tell(all) {
    wait = 0;
    if (!chan || hushed) { pending = {}; return; }
    var m = {from: me};
    if (all || pending.ahead) m.ahead = state.ahead;
    if (all || pending.place) m.place = state.place;
    pending = {};
    try { chan.postMessage(m); } catch (e) {}
  }
  function fire(changed, wasHeard) { heard.forEach(function (fn) { try { fn(state, changed, !!wasHeard); } catch (e) { if (root.console) console.error(e); } }); }
  function set(part, opts) {
    var changed = {}, any = false, quiet = opts && opts.heard;
    if (part && typeof part.ahead === 'number' && isFinite(part.ahead)) {
      var a = Math.abs(part.ahead) < 1000 ? 0 : part.ahead;
      if (a !== state.ahead) { state.ahead = a; changed.ahead = any = true; }
    }
    if (part && 'place' in part) {
      var p = clean(part.place);
      if (!same(p, state.place)) { state.place = p; changed.place = any = true; }
    }
    if (!any) return false;
    if (!quiet) { for (var k in changed) pending[k] = true; if (!wait) wait = setTimeout(tell, 80); }
    fire(changed, quiet);
    return true;
  }
  try {
    chan = new BroadcastChannel('gaia-atlas');
    chan.onmessage = function (e) {
      var d = e.data || {};
      if (d.from === me) return;
      if (d.ask) { if (!hushed && (state.ahead || state.place)) tell(true); return; }   // a face that just opened asks what the others hold
      var part = {};
      if (typeof d.ahead === 'number' && Math.abs(d.ahead - state.ahead) > 500) part.ahead = d.ahead;
      if ('place' in d) part.place = d.place;
      set(part, {heard: true});
    };
    chan.postMessage({from: me, ask: 1});
  } catch (e) { chan = null; }
  root.gaiaOne = {
    id: me, state: state, set: set,
    on: function (fn) { heard.push(fn); },
    hush: function (on) { hushed = !!on; },
    now: function () { return Date.now() + state.ahead; }
  };
})(typeof window !== 'undefined' ? window : globalThis);
