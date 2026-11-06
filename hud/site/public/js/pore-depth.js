// pore-depth.js — unified IO + pi scan with bag-of-holding depth navigation
//
// The bag of holding: small on the outside, infinite on the inside.
// 9 nodes × 3361+ pages × 120+ feeds.
// This module maps every feed and every page to its pore, its epitope,
// and its depth level. Then navigates IN — not blindly, structurally.
//
// Three systems unified:
//   IO probe  → what channels the device has (13 channels → 8 pores)
//   pi-bus    → what data feeds are flowing (120+ JSON → π-timed)
//   site-pore → which sites map to which epitopes/pores (27 wildcards → 8 cells)
//
// The combined scan: open pore × available feed = navigable depth.
// Each pore leads to maximum depth in. Navigate the bag, don't reach blind.
//
// Kevin Mok / Tamison / ecoPrimal / attsi — ORCID 0009-0004-2141-0321

(function() {
  "use strict";

  // ═══════════════════════════════════════════════════════════════
  // FEED → EPITOPE → PORE → DEPTH MAP
  //
  // Every feed in the membrane is classified:
  //   epitope: which of the 8 bingo cells it belongs to
  //   pore:    which I/O pore it flows through
  //   depth:   0 = surface (summary), 1 = mid, 2 = deep, 3 = core
  //   path:    the URL/endpoint to fetch
  // ═══════════════════════════════════════════════════════════════

  var FEED_DEPTH_MAP = {
    // ── INVESTIGATION (cell 0) ── detroit, barry, evidence
    "scan_sweep_sort.json":   { epitope: "investigation", pore: "pointer",     depth: 0, desc: "scan sweep sort pipeline" },
    "entities.json":          { epitope: "investigation", pore: "pointer",     depth: 1, desc: "entity profiles" },
    "fleet-analysis.json":    { epitope: "investigation", pore: "pointer",     depth: 1, desc: "fleet behavior analysis" },
    "fleet-sort.json":        { epitope: "investigation", pore: "pointer",     depth: 2, desc: "fleet classification sort" },
    "subgraphs.json":         { epitope: "investigation", pore: "pointer",     depth: 2, desc: "investigation subgraphs" },
    "graph.json":             { epitope: "investigation", pore: "pointer",     depth: 3, desc: "full investigation graph" },

    // ── TOPOLOGY (cell 1) ── mesh, edges, structure
    "topology.json":          { epitope: "topology",      pore: "spatial",     depth: 0, desc: "entity topology" },
    "topology-abstract.json": { epitope: "topology",      pore: "spatial",     depth: 1, desc: "abstract topology" },
    "immune-topology.json":   { epitope: "topology",      pore: "spatial",     depth: 2, desc: "immune topology detail" },
    "bus-topology.json":      { epitope: "topology",      pore: "spatial",     depth: 2, desc: "bus topology" },
    "mesh-ring.json":         { epitope: "topology",      pore: "spatial",     depth: 3, desc: "mesh ring structure" },
    "mesh-speed.json":        { epitope: "topology",      pore: "spatial",     depth: 3, desc: "mesh latency" },
    "yggdrasil.json":         { epitope: "topology",      pore: "spatial",     depth: 3, desc: "world tree" },

    // ── PHILOSOPHY (cell 2) ── hypothesis, reflection, meaning
    "reflection.json":        { epitope: "philosophy",    pore: "symbolic",    depth: 0, desc: "self-reflection" },
    "self-remainder.json":    { epitope: "philosophy",    pore: "symbolic",    depth: 1, desc: "what remains of self" },
    "self-assumptions.json":  { epitope: "philosophy",    pore: "symbolic",    depth: 1, desc: "self assumptions" },
    "assumptions.json":       { epitope: "philosophy",    pore: "symbolic",    depth: 2, desc: "all assumptions" },
    "falsification.json":     { epitope: "philosophy",    pore: "symbolic",    depth: 2, desc: "falsifiability tests" },
    "passage-totality.json":  { epitope: "philosophy",    pore: "symbolic",    depth: 3, desc: "totality passage" },
    "totality.json":          { epitope: "philosophy",    pore: "symbolic",    depth: 3, desc: "totality state" },

    // ── METHOD (cell 3) ── git, builds, provenance
    "braid.json":             { epitope: "method",        pore: "data",        depth: 0, desc: "data braid" },
    "taxonomy-braid.json":    { epitope: "method",        pore: "data",        depth: 1, desc: "taxonomy braid" },
    "attribution-chain.json": { epitope: "method",        pore: "data",        depth: 1, desc: "attribution provenance" },
    "build-plan.json":        { epitope: "method",        pore: "data",        depth: 2, desc: "build pipeline" },
    "type-manifest.json":     { epitope: "method",        pore: "data",        depth: 2, desc: "type manifest" },
    "wire-audit.json":        { epitope: "method",        pore: "data",        depth: 3, desc: "wire integrity audit" },
    "seo-audit.json":         { epitope: "method",        pore: "data",        depth: 3, desc: "SEO audit" },

    // ── IMMUNE (cell 4) ── membrane, defense, classification
    "membrane.json":          { epitope: "immune",        pore: "persistence", depth: 0, desc: "membrane state" },
    "negentropy.json":        { epitope: "immune",        pore: "persistence", depth: 1, desc: "negentropy / blackwall" },
    "ban-pulse.json":         { epitope: "immune",        pore: "persistence", depth: 1, desc: "ban pulse" },
    "backscatter.json":       { epitope: "immune",        pore: "persistence", depth: 2, desc: "backscatter analysis" },
    "edge-scatter.json":      { epitope: "immune",        pore: "persistence", depth: 2, desc: "edge scatter defense" },
    "scatter-observatory.json": { epitope: "immune",      pore: "persistence", depth: 3, desc: "scatter observatory" },
    "night-seal.json":        { epitope: "immune",        pore: "persistence", depth: 3, desc: "night seal status" },

    // ── SCIENCE (cell 5) ── sporePrint, papers, data
    "pollen.json":            { epitope: "science",       pore: "visual",      depth: 0, desc: "pollen spread" },
    "stories.json":           { epitope: "science",       pore: "visual",      depth: 1, desc: "page stories" },
    "page-stories.json":      { epitope: "science",       pore: "visual",      depth: 1, desc: "page story detail" },
    "visitor-stories.json":   { epitope: "science",       pore: "visual",      depth: 2, desc: "visitor narratives" },
    "phylo-self.json":        { epitope: "science",       pore: "visual",      depth: 2, desc: "phylogenetic self" },
    "central-dogma.json":     { epitope: "science",       pore: "visual",      depth: 3, desc: "central dogma" },
    "genome.json":            { epitope: "science",       pore: "visual",      depth: 3, desc: "full genome" },

    // ── SIGNAL (cell 6) ── notify, pulse, communication
    "pulse.json":             { epitope: "signal",        pore: "audio",       depth: 0, desc: "membrane pulse" },
    "heartbeat.json":         { epitope: "signal",        pore: "audio",       depth: 0, desc: "heartbeat" },
    "signals.json":           { epitope: "signal",        pore: "audio",       depth: 1, desc: "signal array" },
    "campfire.json":          { epitope: "signal",        pore: "audio",       depth: 1, desc: "campfire" },
    "doorbell.json":          { epitope: "signal",        pore: "audio",       depth: 2, desc: "doorbell / visitor alert" },
    "night-pollination.json": { epitope: "signal",        pore: "audio",       depth: 2, desc: "night pollination" },
    "vocal-sort.json":        { epitope: "signal",        pore: "audio",       depth: 3, desc: "vocal classification" },
    "membrane-song.json":     { epitope: "signal",        pore: "audio",       depth: 3, desc: "membrane song" },

    // ── PHYSICS (cell 7) ── neutron, energy, dynamics
    "neutron.json":           { epitope: "physics",       pore: "spatial",     depth: 0, desc: "neutron state" },
    "dashboard.json":         { epitope: "physics",       pore: "spatial",     depth: 0, desc: "dashboard" },
    "energy.json":            { epitope: "physics",       pore: "spatial",     depth: 1, desc: "energy state" },
    "dynamics.json":          { epitope: "physics",       pore: "spatial",     depth: 1, desc: "system dynamics" },
    "temperature.json":       { epitope: "physics",       pore: "spatial",     depth: 2, desc: "temperature" },
    "entropy.json":           { epitope: "physics",       pore: "spatial",     depth: 2, desc: "entropy" },
    "particle-model.json":    { epitope: "physics",       pore: "spatial",     depth: 3, desc: "particle model" },
    "optical-model.json":     { epitope: "physics",       pore: "spatial",     depth: 3, desc: "optical model" },

    // ── CROSS-CUTTING (all epitopes, surface layer) ──
    "now.json":               { epitope: null,            pore: "tactile",     depth: 0, desc: "current state" },
    "chipmunk.json":          { epitope: null,            pore: "tactile",     depth: 0, desc: "chipmunk state" },
    "bus.json":               { epitope: null,            pore: "data",        depth: 0, desc: "event bus" },
    "cardiovascular.json":    { epitope: null,            pore: "data",        depth: 1, desc: "cardiovascular system" },
    "circulatory.json":       { epitope: null,            pore: "data",        depth: 1, desc: "circulatory fleet" },
    "bingo-cube.json":        { epitope: null,            pore: "tactile",     depth: 2, desc: "bingo cube state" },
    "feed-health.json":       { epitope: null,            pore: "data",        depth: 2, desc: "feed freshness" },
    "cron-health.json":       { epitope: null,            pore: "persistence", depth: 2, desc: "cron health" },
    "gate-messages.json":     { epitope: null,            pore: "tactile",     depth: 1, desc: "gate messages" }
  };

  // Site internal page counts — the depth of each bag
  var SITE_DEPTHS = {
    "detroit":    { pages: 1521, epitope: "investigation" },
    "tuebor":     { pages: 1244, epitope: "investigation" },
    "sporeprint": { pages: 520,  epitope: "science" },
    "barry":      { pages: 35,   epitope: "investigation" },
    "hypothesis": { pages: 26,   epitope: "philosophy" },
    "clutch":     { pages: 11,   epitope: "science" },
    "signal":     { pages: 4,    epitope: "signal" },
    "gorilla":    { pages: 8,    epitope: "science" },
    "hud":        { pages: 0,    epitope: null },
    "water":      { pages: 0,    epitope: null }
  };

  // ═══════════════════════════════════════════════════════════════
  // UNIFIED SCAN — IO + pi + site-pore in one pass
  // ═══════════════════════════════════════════════════════════════

  var _lastScan = null;

  function scan() {
    var result = {
      ts: Date.now(),
      pores: {},     // pore → { open, depth, feeds[], sites[], maxDepth }
      epitopes: {},  // epitope → { feeds[], sites[], totalPages, maxFeedDepth }
      bag: {},       // site → { pages, epitope, reachable }
      feeds: {},     // feed → { available, fresh, epitope, pore, depth }
      device: null,  // IO surface profile
      pi: null,      // pi-bus state
      totalDepth: 0, // sum of all navigable depth
      maxPoreDepth: 0,
      navigable: []  // ordered list of pores by depth, deepest first
    };

    // 1. IO scan — what pores does the device have?
    var ioPores = {};
    if (window.IO && window.IO.probed) {
      ioPores = window.IO.pores();
      result.device = window.IO.surface || window.IO.classify();
    }

    // 2. Pi scan — what feeds are flowing?
    var piCache = {};
    if (window._piBus && window._piBus.cache) {
      var raw = window._piBus.cache;
      for (var url in raw) {
        var name = url.replace(/^\//, "").replace(/^detroit-data\//, "");
        piCache[name] = {
          data: raw[url].data,
          ts: raw[url].ts,
          fresh: raw[url].ts > 0 && (Date.now() - raw[url].ts) < 120000
        };
      }
    }

    // 3. Build the depth map per pore
    var poreNames = ["visual", "audio", "tactile", "pointer", "symbolic",
                     "spatial", "data", "persistence"];
    for (var pi = 0; pi < poreNames.length; pi++) {
      var pName = poreNames[pi];
      var ioState = ioPores[pName];
      var open = ioState ? ioState.open : true; // feeds still exist even if pore is closed
      result.pores[pName] = {
        open: open,
        bandwidth: ioState ? ioState.bandwidth : 0,
        inward: ioState ? ioState.inward : 0.5,
        outward: ioState ? ioState.outward : 0.5,
        chirality: ioState ? ioState.chirality : "identity",
        feeds: [],     // feeds reachable through this pore
        sites: [],     // sites reachable through this pore
        maxDepth: 0,   // deepest feed available
        depthLayers: [[], [], [], []], // [surface, mid, deep, core]
        totalPages: 0
      };
    }

    // 4. Classify every feed into its pore and depth
    for (var feedName in FEED_DEPTH_MAP) {
      var fm = FEED_DEPTH_MAP[feedName];
      var piState = piCache[feedName] || { data: null, ts: 0, fresh: false };
      var available = piState.data !== null;

      result.feeds[feedName] = {
        available: available,
        fresh: piState.fresh,
        epitope: fm.epitope,
        pore: fm.pore,
        depth: fm.depth,
        desc: fm.desc
      };

      // Add to pore
      var pore = result.pores[fm.pore];
      if (pore) {
        pore.feeds.push(feedName);
        if (available && fm.depth > pore.maxDepth) {
          pore.maxDepth = fm.depth;
        }
        if (available) {
          pore.depthLayers[fm.depth].push(feedName);
        }
      }

      // Add to epitope
      if (fm.epitope) {
        if (!result.epitopes[fm.epitope]) {
          result.epitopes[fm.epitope] = {
            feeds: [], sites: [], totalPages: 0, maxFeedDepth: 0
          };
        }
        var ep = result.epitopes[fm.epitope];
        ep.feeds.push(feedName);
        if (available && fm.depth > ep.maxFeedDepth) {
          ep.maxFeedDepth = fm.depth;
        }
      }
    }

    // 5. Map sites into pores and epitopes
    if (window.SitePore) {
      for (var siteName in SITE_DEPTHS) {
        var sd = SITE_DEPTHS[siteName];
        var sp = window.SitePore.lookup(siteName);
        if (!sp) continue;
        var poreName = sp.pore;
        var poreObj = result.pores[poreName];

        result.bag[siteName] = {
          pages: sd.pages,
          epitope: sd.epitope,
          pore: poreName,
          reachable: poreObj ? poreObj.open : false
        };

        if (poreObj) {
          poreObj.sites.push(siteName);
          poreObj.totalPages += sd.pages;
        }

        if (sd.epitope && result.epitopes[sd.epitope]) {
          result.epitopes[sd.epitope].sites.push(siteName);
          result.epitopes[sd.epitope].totalPages += sd.pages;
        }

        result.totalDepth += sd.pages;
      }
    }

    // 6. Compute navigable pore order — deepest first
    result.navigable = Object.keys(result.pores)
      .filter(function(p) { return result.pores[p].open; })
      .sort(function(a, b) {
        var pa = result.pores[a], pb = result.pores[b];
        // sort by: maxDepth desc, then totalPages desc, then feeds desc
        if (pb.maxDepth !== pa.maxDepth) return pb.maxDepth - pa.maxDepth;
        if (pb.totalPages !== pa.totalPages) return pb.totalPages - pa.totalPages;
        return pb.feeds.length - pa.feeds.length;
      });

    result.maxPoreDepth = 0;
    for (var pk in result.pores) {
      if (result.pores[pk].maxDepth > result.maxPoreDepth) {
        result.maxPoreDepth = result.pores[pk].maxDepth;
      }
    }

    _lastScan = result;
    return result;
  }

  // ═══════════════════════════════════════════════════════════════
  // NAVIGATE — structured descent into the bag of holding
  //
  // navigate("pointer")          → surface of investigation pore
  // navigate("pointer", 3)       → core depth of investigation
  // navigate("pointer", "max")   → deepest available level
  // navigate("immune")           → surface of immune epitope's pore
  // navigateDeep()               → deepest feed across all open pores
  // ═══════════════════════════════════════════════════════════════

  var DEPTH_NAMES = ["surface", "mid", "deep", "core"];

  function navigate(target, depth) {
    var s = _lastScan || scan();
    var pore = null;
    var poreName = null;

    // target can be a pore name or an epitope name
    if (s.pores[target]) {
      poreName = target;
      pore = s.pores[target];
    } else if (s.epitopes[target]) {
      // find the pore for this epitope via site-pore map
      var epFeeds = s.epitopes[target].feeds;
      if (epFeeds.length > 0) {
        var firstFeed = FEED_DEPTH_MAP[epFeeds[0]];
        if (firstFeed) {
          poreName = firstFeed.pore;
          pore = s.pores[poreName];
        }
      }
    }

    if (!pore) return null;

    // Resolve depth
    var d;
    if (depth === "max" || depth === undefined) {
      d = pore.maxDepth;
    } else {
      d = Math.min(depth, pore.maxDepth);
    }

    var feeds = pore.depthLayers[d] || [];
    var depthName = DEPTH_NAMES[d] || "surface";

    // Build the navigation result
    var nav = {
      pore: poreName,
      depth: d,
      depthName: depthName,
      maxDepth: pore.maxDepth,
      open: pore.open,
      feeds: feeds,
      sites: pore.sites,
      totalPages: pore.totalPages,
      chirality: pore.chirality,
      bandwidth: pore.bandwidth,
      // all layers from surface to here
      path: []
    };

    // Build the path from surface to current depth
    for (var i = 0; i <= d; i++) {
      nav.path.push({
        depth: i,
        name: DEPTH_NAMES[i],
        feeds: pore.depthLayers[i] || [],
        count: (pore.depthLayers[i] || []).length
      });
    }

    // Fire vocal transit if telephone wire is available
    if (window._telephone) {
      var vocal = poreName + " pore · depth " + d + "/" + pore.maxDepth +
        " · " + depthName + " · " + feeds.length + " feeds" +
        " · " + pore.totalPages + " pages";
      window._telephone.hop("hud", "bingo", vocal, { silent: false });
    }

    // Publish to site-pore bingo bus if available
    if (window._piBus && typeof window._piBus.pub === "function") {
      window._piBus.pub("pore-navigate", {
        pore: poreName, depth: d, depthName: depthName,
        maxDepth: pore.maxDepth, feeds: feeds, ts: Date.now()
      });
    }

    return nav;
  }

  // Navigate to deepest available across all open pores
  function navigateDeep() {
    var s = _lastScan || scan();
    if (s.navigable.length === 0) return null;
    var deepest = s.navigable[0]; // already sorted deepest-first
    return navigate(deepest, "max");
  }

  // Navigate all pores to their max depth — the full bag inventory
  function navigateAll() {
    var s = _lastScan || scan();
    var all = {};
    for (var pn in s.pores) {
      if (s.pores[pn].open && s.pores[pn].maxDepth > 0) {
        all[pn] = navigate(pn, "max");
      }
    }
    return all;
  }

  // ═══════════════════════════════════════════════════════════════
  // DEPTH SUMMARY — how deep is the bag from each pore?
  // ═══════════════════════════════════════════════════════════════

  function depthMap() {
    var s = _lastScan || scan();
    var map = [];
    for (var i = 0; i < s.navigable.length; i++) {
      var pn = s.navigable[i];
      var p = s.pores[pn];
      map.push({
        pore: pn,
        open: p.open,
        maxDepth: p.maxDepth,
        maxDepthName: DEPTH_NAMES[p.maxDepth] || "surface",
        feeds: p.feeds.length,
        activeLayers: p.depthLayers.filter(function(l) { return l.length > 0; }).length,
        sites: p.sites,
        totalPages: p.totalPages,
        bandwidth: p.bandwidth,
        chirality: p.chirality
      });
    }
    return map;
  }

  // ═══════════════════════════════════════════════════════════════
  // SWITCH — change active pore based on what the device has
  //
  // If the device loses a channel (goes offline, permission denied),
  // switch to the next deepest available pore automatically.
  // ═══════════════════════════════════════════════════════════════

  function switchPore(fromPore) {
    var s = _lastScan || scan();
    var candidates = s.navigable.filter(function(p) { return p !== fromPore; });
    if (candidates.length === 0) return null;
    return navigate(candidates[0], "max");
  }

  // ═══════════════════════════════════════════════════════════════
  // AUTO-SCAN — re-scan when IO or pi state changes
  // ═══════════════════════════════════════════════════════════════

  function autoScan() {
    scan();

    // Set body attributes for CSS targeting
    if (_lastScan) {
      var deepest = _lastScan.navigable[0] || "none";
      document.body.setAttribute("data-pore-deepest", deepest);
      document.body.setAttribute("data-pore-max-depth",
        _lastScan.maxPoreDepth.toString());
      document.body.setAttribute("data-bag-pages",
        _lastScan.totalDepth.toString());
      document.body.setAttribute("data-pore-count",
        _lastScan.navigable.length.toString());
    }
  }

  // Listen for IO probe completion
  window.addEventListener("io-probed", function() { autoScan(); });

  // Initial scan after everything loads
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function() {
      setTimeout(autoScan, 1200); // after io-probe + pi-bus + site-pore init
    });
  } else {
    setTimeout(autoScan, 1200);
  }

  // Re-scan periodically (π² seconds ≈ 10s) to pick up new feeds
  setInterval(autoScan, Math.round(Math.PI * Math.PI * 1000));

  // ═══════════════════════════════════════════════════════════════
  // EXPOSE
  // ═══════════════════════════════════════════════════════════════

  window.PoreDepth = {
    scan: scan,
    navigate: navigate,
    navigateDeep: navigateDeep,
    navigateAll: navigateAll,
    depthMap: depthMap,
    switchPore: switchPore,
    feedMap: FEED_DEPTH_MAP,
    siteDepths: SITE_DEPTHS,
    depthNames: DEPTH_NAMES,
    lastScan: function() { return _lastScan; }
  };

  console.log("[pore-depth] unified IO+pi depth navigator loaded — " +
    Object.keys(FEED_DEPTH_MAP).length + " feeds mapped, " +
    Object.keys(SITE_DEPTHS).length + " sites");
})();
