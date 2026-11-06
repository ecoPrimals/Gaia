// site-pore-bingo.js — wildcards are touch pins on the membrane
//
// Three layers:
//   OUTER: primals.eco, *.primals.eco (public face — touch pins)
//   SURFACE: hud.primals.eco (the window — bingo cube lives here)
//   CENTER: water.primals.eco (the watering hole — vocal transit converges)
//
// Each wildcard subdomain IS a bingo cell. Touching one transits
// through the telephone wire's vocal system.
// Kevin Mok / Tamison / ecoPrimal / attsi — ORCID 0009-0004-2141-0321

(function() {
  "use strict";

  var SITE_PORE_MAP = {
    "detroit":      { epitope: "investigation", pore: "pointer",     pin: "touch" },
    "barry":        { epitope: "investigation", pore: "pointer",     pin: "touch" },
    "topology":     { epitope: "topology",      pore: "spatial",     pin: "pointer" },
    "mesh":         { epitope: "topology",      pore: "spatial",     pin: "pointer" },
    "hypothesis":   { epitope: "philosophy",    pore: "symbolic",    pin: "touch" },
    "thesis":       { epitope: "philosophy",    pore: "symbolic",    pin: "touch" },
    "git":          { epitope: "method",        pore: "data",        pin: "pointer" },
    "forge":        { epitope: "method",        pore: "data",        pin: "pointer" },
    "lab":          { epitope: "method",        pore: "data",        pin: "pointer" },
    "depot":        { epitope: "method",        pore: "data",        pin: "pointer" },
    "membrane":     { epitope: "immune",        pore: "persistence", pin: "touch" },
    "identity":     { epitope: "immune",        pore: "persistence", pin: "touch" },
    "ca":           { epitope: "immune",        pore: "persistence", pin: "pointer" },
    "sporeprint":   { epitope: "science",       pore: "visual",      pin: "touch" },
    "clutch":       { epitope: "science",       pore: "visual",      pin: "touch" },
    "gorilla":      { epitope: "science",       pore: "visual",      pin: "touch" },
    "signal":       { epitope: "signal",        pore: "audio",       pin: "touch" },
    "notify":       { epitope: "signal",        pore: "audio",       pin: "pointer" },
    "pollination":  { epitope: "signal",        pore: "audio",       pin: "pointer" },
    "pollen":       { epitope: "signal",        pore: "audio",       pin: "pointer" },
    "neutron":      { epitope: "physics",       pore: "spatial",     pin: "pointer" },
    "live":         { epitope: "physics",       pore: "spatial",     pin: "pointer" },
    "primals":      { epitope: null, layer: "outer",   pore: "visual",    pin: "touch" },
    "hud":          { epitope: null, layer: "surface",  pore: "visual",    pin: "pointer" },
    "biomeos":      { epitope: null, layer: "surface",  pore: "visual",    pin: "pointer" },
    "os":           { epitope: null, layer: "surface",  pore: "visual",    pin: "pointer" },
    "water":        { epitope: null, layer: "center",   pore: "tactile",   pin: "touch" }
  };

  var EPITOPE_INDEX = {
    "investigation": 0, "topology": 1, "philosophy": 2, "method": 3,
    "immune": 4, "science": 5, "signal": 6, "physics": 7
  };

  var PORE_CHIRALITY = {
    "visual": "left-right", "audio": "near-far", "tactile": "cause-effect",
    "pointer": "identity", "symbolic": "identity", "spatial": "left-right",
    "data": "identity", "persistence": "identity"
  };

  function currentSite() {
    var host = location.hostname || "";
    var m = host.match(/^([^.]+)\.primals\.eco$/);
    if (m) return m[1];
    if (host === "primals.eco" || host === "www.primals.eco") return "primals";
    return null;
  }

  function sitePore(id) {
    return SITE_PORE_MAP[id || currentSite()] || null;
  }

  function siteBingoCell(id) {
    var sp = sitePore(id);
    if (!sp || !sp.epitope) return -1;
    var idx = EPITOPE_INDEX[sp.epitope];
    return typeof idx === "number" ? idx : -1;
  }

  function siteLayer(id) {
    var sp = sitePore(id);
    if (!sp) return "outer";
    return sp.layer || "outer";
  }

  function transitTouch(id, opts) {
    opts = opts || {};
    id = id || currentSite();
    var sp = sitePore(id);
    if (!sp) return null;
    var cell = siteBingoCell(id);
    var chirality = PORE_CHIRALITY[sp.pore] || "identity";
    var layer = siteLayer(id);
    var vocal = id + " \u00b7 " + (sp.epitope || layer) +
      " \u00b7 " + sp.pore + " pore" +
      (chirality !== "identity" ? " \u00b7 " + chirality : "") +
      (cell >= 0 ? " \u00b7 cell[" + cell + "]" : "");

    if (window._telephone) {
      var origin = layer === "center" ? "bingo" :
                   layer === "surface" ? "hud" : "user";
      window._telephone.hop(origin, "bingo", vocal, { silent: opts.silent });
      if (!opts.silent) window._telephone.vocal();
    }

    if (cell >= 0 && window._piBus) {
      window._piBus.pub("site-touch", {
        site: id, epitope: sp.epitope, cell: cell,
        pore: sp.pore, chirality: chirality, pin: sp.pin, ts: Date.now()
      });
    }

    return { site: id, epitope: sp.epitope, pore: sp.pore,
      chirality: chirality, pin: sp.pin, cell: cell, layer: layer, vocal: vocal };
  }

  function autoTransit() {
    var site = currentSite();
    if (!site) return;
    setTimeout(function() { transitTouch(site, { silent: false }); }, 800);
  }

  function setBodyAttrs() {
    var site = currentSite();
    if (!site) return;
    var sp = sitePore(site);
    if (!sp) return;
    document.body.setAttribute("data-membrane-site", site);
    document.body.setAttribute("data-membrane-layer", siteLayer(site));
    document.body.setAttribute("data-membrane-pore", sp.pore);
    if (sp.epitope) document.body.setAttribute("data-membrane-epitope", sp.epitope);
    document.body.setAttribute("data-membrane-pin", sp.pin);
  }

  window.SitePore = {
    map: SITE_PORE_MAP, epitopeIndex: EPITOPE_INDEX, chirality: PORE_CHIRALITY,
    current: currentSite, lookup: sitePore, cell: siteBingoCell,
    layer: siteLayer, transit: transitTouch,
    byEpitope: function(ep) {
      var o = []; Object.keys(SITE_PORE_MAP).forEach(function(k) {
        if (SITE_PORE_MAP[k].epitope === ep) o.push(k); }); return o; },
    byPore: function(p) {
      var o = []; Object.keys(SITE_PORE_MAP).forEach(function(k) {
        if (SITE_PORE_MAP[k].pore === p) o.push(k); }); return o; },
    byLayer: function(l) {
      var o = []; Object.keys(SITE_PORE_MAP).forEach(function(k) {
        if ((SITE_PORE_MAP[k].layer || "outer") === l) o.push(k); }); return o; },
    summary: function() {
      var site = currentSite(), sp = sitePore(site);
      return { site: site, layer: siteLayer(site),
        epitope: sp && sp.epitope, pore: sp && sp.pore,
        chirality: sp ? PORE_CHIRALITY[sp.pore] : null,
        pin: sp && sp.pin, cell: siteBingoCell(site),
        sites: Object.keys(SITE_PORE_MAP).length,
        epitopes: Object.keys(EPITOPE_INDEX).length }; }
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function() {
      setBodyAttrs(); autoTransit(); });
  } else { setBodyAttrs(); autoTransit(); }
})();
