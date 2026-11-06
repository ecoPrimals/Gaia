/**
 * CNS Router — Central Nervous System for the primals.eco surface network.
 *
 * The hidden brain. Routes itinerables (visitors, data, attention) between
 * surfaces without dropping them blind into the black hole.
 *
 * Transmission model:
 *   Engine (human investigation) always spins.
 *   Clutch (clutch.primals.eco) engages/disengages gears.
 *   Gears select force profile (investigation/science/observation).
 *   CNS routes — this file.
 *
 * CNS types (from the nervous system):
 *   cortex     — thinking surfaces (clutch, sporeprint, tuebor)
 *   sensory    — observation surfaces (hud, water, signal, gorilla, live)
 *   motor      — action surfaces (detroit, barry, lansing)
 *   autonomic  — hidden plumbing (membrane, neutron, mesh, etc.)
 *   immune     — defense maze (bloom, thymus, opsonize, etc.)
 *
 * Kevin Mok / Tamison / ecoPrimal / attsi
 * ORCID 0009-0004-2141-0321
 */

(function () {
  "use strict";

  /* ── Surface registry ── */
  const SURFACES = {
    // investigation gear (1st)
    detroit:    { gear: "investigation", cns: "motor",     depth: 4, pages: 424,  domain: "detroit.primals.eco" },
    barry:      { gear: "investigation", cns: "motor",     depth: 2, pages: 35,   domain: "barry.primals.eco" },
    clutch:     { gear: "investigation", cns: "prefrontal",depth: 1, pages: 10,   domain: "clutch.primals.eco" },
    tuebor:     { gear: "investigation", cns: "cortex",    depth: 5, pages: 1219, domain: "tuebor.primals.eco" },
    lansing:    { gear: "investigation", cns: "motor",     depth: 0, pages: 0,    domain: "lansing.primals.eco" },
    // science gear (2nd)
    sporeprint: { gear: "science",       cns: "cortex",    depth: 4, pages: 510,  domain: "sporeprint.primals.eco" },
    thesis:     { gear: "science",       cns: "cortex",    depth: 1, pages: 2,    domain: "thesis.primals.eco" },
    hypothesis: { gear: "science",       cns: "cortex",    depth: 0, pages: 0,    domain: "hypothesis.primals.eco" },
    // observation gear (3rd)
    hud:        { gear: "observation",   cns: "sensory",   depth: 2, pages: 20,   domain: "hud.primals.eco" },
    water:      { gear: "observation",   cns: "sensory",   depth: 1, pages: 1,    domain: "water.primals.eco" },
    signal:     { gear: "observation",   cns: "sensory",   depth: 1, pages: 3,    domain: "signal.primals.eco" },
    gorilla:    { gear: "observation",   cns: "sensory",   depth: 2, pages: 22,   domain: "gorilla.primals.eco" },
    live:       { gear: "observation",   cns: "sensory",   depth: 0, pages: 0,    domain: "live.primals.eco" },
    // infrastructure gear (4th — hidden)
    git:        { gear: "infrastructure",cns: "autonomic", depth: 0, pages: 0,    domain: "git.primals.eco" },
    membrane:   { gear: "infrastructure",cns: "autonomic", depth: 0, pages: 0,    domain: "membrane.primals.eco" },
    neutron:    { gear: "infrastructure",cns: "autonomic", depth: 0, pages: 0,    domain: "neutron.primals.eco" },
    notify:     { gear: "infrastructure",cns: "autonomic", depth: 0, pages: 0,    domain: "notify.primals.eco" },
    mesh:       { gear: "infrastructure",cns: "autonomic", depth: 0, pages: 0,    domain: "mesh.primals.eco" },
    pollen:     { gear: "infrastructure",cns: "autonomic", depth: 0, pages: 0,    domain: "pollination.primals.eco" },
    ca:         { gear: "infrastructure",cns: "autonomic", depth: 0, pages: 0,    domain: "ca.primals.eco" },
    depot:      { gear: "infrastructure",cns: "autonomic", depth: 0, pages: 0,    domain: "depot.primals.eco" },
    nestgate:   { gear: "infrastructure",cns: "autonomic", depth: 0, pages: 0,    domain: "nestgate.io" },
  };

  /* ── Feed map: what flows where ── */
  const FEEDS = {
    detroit:    { to: ["clutch","barry","tuebor","signal"],       from: ["clutch","tuebor","sporeprint"] },
    barry:      { to: ["clutch","detroit"],                       from: ["clutch","detroit","signal"] },
    clutch:     { to: ["detroit","barry","tuebor","sporeprint","signal"], from: ["detroit","barry","tuebor","sporeprint","gorilla"] },
    tuebor:     { to: ["detroit","barry","clutch","signal","sporeprint"], from: ["detroit","clutch","sporeprint","gorilla","signal"] },
    sporeprint: { to: ["thesis","hypothesis","clutch","detroit","tuebor"], from: ["hypothesis","thesis","hud"] },
    thesis:     { to: ["sporeprint","hypothesis"],                from: ["sporeprint"] },
    hypothesis: { to: ["sporeprint","thesis"],                    from: ["sporeprint"] },
    hud:        { to: ["water","signal","gorilla","neutron"],     from: ["water","neutron","membrane","live"] },
    water:      { to: ["hud","neutron"],                          from: ["hud","neutron","membrane"] },
    signal:     { to: ["gorilla","clutch","detroit"],             from: ["gorilla","hud","membrane"] },
    gorilla:    { to: ["signal","hud","clutch"],                  from: ["membrane","signal","hud"] },
    live:       { to: ["hud","signal"],                           from: ["membrane"] },
    membrane:   { to: ["hud","water","signal","live"],            from: ["neutron","pollen"] },
    neutron:    { to: ["hud","water","membrane"],                 from: ["membrane"] },
  };

  /* ── Gear transitions (clutch actions) ── */
  const SHIFTS = {
    "investigation→science":   { action: "press",     path: "clutch.contribute → sporeprint.methodology" },
    "science→investigation":   { action: "release",   path: "sporeprint.methodology → clutch.graph" },
    "observation→investigation": { action: "downshift", path: "signal → clutch.graph" },
    "investigation→observation": { action: "upshift",   path: "tuebor → signal OR hud" },
    "any→infrastructure":      { action: "neutral",   path: "no human-facing entry" },
  };

  /* ── Topo sort tiers ── */
  const TOPO = [
    { tier: 0, name: "autonomic", ids: ["ca","nestgate","depot"] },
    { tier: 1, name: "nervous",   ids: ["membrane","neutron","mesh","notify"] },
    { tier: 2, name: "immune",    ids: [] }, // 12 honeycomb subdomains, not in SURFACES
    { tier: 3, name: "sensory",   ids: ["hud","water","signal","gorilla","live"] },
    { tier: 4, name: "motor",     ids: ["detroit","barry","lansing"] },
    { tier: 5, name: "cortex",    ids: ["sporeprint","thesis","hypothesis"] },
    { tier: 6, name: "prefrontal",ids: ["clutch","tuebor"] },
    { tier: 7, name: "source",    ids: ["git","pollen"] },
  ];

  /* ── Where am I? ── */
  function identify() {
    const host = location.hostname;
    for (const [id, s] of Object.entries(SURFACES)) {
      if (host === s.domain) return { id, ...s };
      if (s.aliases && s.aliases.includes(host)) return { id, ...s };
    }
    // on-demand TLS catch-all — check subdomain
    const sub = host.replace(".primals.eco", "");
    if (SURFACES[sub]) return { id: sub, ...SURFACES[sub] };
    return null;
  }

  /* ── What gear am I in? ── */
  function currentGear() {
    const here = identify();
    return here ? here.gear : "unknown";
  }

  /* ── What CNS type am I? ── */
  function cnsType() {
    const here = identify();
    return here ? here.cns : "unknown";
  }

  /* ── What feeds me? What do I feed? ── */
  function connections() {
    const here = identify();
    if (!here || !FEEDS[here.id]) return { to: [], from: [] };
    const feed = FEEDS[here.id];
    return {
      to:   feed.to.map(id => ({ id, ...SURFACES[id] })),
      from: feed.from.map(id => ({ id, ...SURFACES[id] })),
    };
  }

  /* ── How to shift gears from here ── */
  function availableShifts() {
    const gear = currentGear();
    if (gear === "unknown") return [];
    const shifts = [];
    for (const [key, val] of Object.entries(SHIFTS)) {
      const [from] = key.split("→");
      if (from === gear || from === "any") {
        shifts.push({ transition: key, ...val });
      }
    }
    return shifts;
  }

  /* ── Navigate to a surface (with depth guard) ── */
  function navigateTo(targetId, opts = {}) {
    const target = SURFACES[targetId];
    if (!target) return null;

    const maxDepth = opts.maxDepth ?? 2;
    const here = identify();

    // depth guard: warn if target is a black hole
    if (target.depth > maxDepth && !opts.force) {
      const msg = `⚠ ${targetId} has depth ${target.depth} (${target.pages} pages). ` +
                  `Max safe depth is ${maxDepth}. Pass {force:true} to override.`;
      console.warn("[CNS]", msg);
      if (window._chipmunk && typeof window._chipmunk.say === "function") {
        window._chipmunk.say(msg);
      }
      return { blocked: true, reason: "depth_exceeded", target: targetId, depth: target.depth, pages: target.pages };
    }

    // gear shift detection
    if (here && here.gear !== target.gear) {
      const key = `${here.gear}→${target.gear}`;
      const shift = SHIFTS[key];
      if (shift) {
        console.log("[CNS] gear shift:", key, shift.action);
        if (window._chipmunk && typeof window._chipmunk.say === "function") {
          window._chipmunk.say(`${shift.action} — shifting from ${here.gear} to ${target.gear}`);
        }
      }
    }

    const url = `https://${target.domain}${opts.path || "/"}`;
    if (opts.dryRun) return { url, target: targetId, gear: target.gear, cns: target.cns, depth: target.depth };

    location.href = url;
    return { navigating: true, url };
  }

  /* ── Topo-sorted surface list ── */
  function topoSort() {
    const sorted = [];
    for (const tier of TOPO) {
      for (const id of tier.ids) {
        if (SURFACES[id]) {
          sorted.push({ tier: tier.tier, tierName: tier.name, id, ...SURFACES[id] });
        }
      }
    }
    return sorted;
  }

  /* ── Summary for current position ── */
  function whereAmI() {
    const here = identify();
    if (!here) return { unknown: true, host: location.hostname };
    const conn = connections();
    const shifts = availableShifts();
    return {
      surface: here.id,
      domain: here.domain,
      gear: here.gear,
      cns: here.cns,
      depth: here.depth,
      pages: here.pages,
      feedsTo: conn.to.map(s => s.id),
      fedBy: conn.from.map(s => s.id),
      shifts: shifts.map(s => s.transition),
    };
  }

  /* ── Set body attributes for CSS/JS consumption ── */
  function stamp() {
    const here = identify();
    if (!here) return;
    document.body.setAttribute("data-cns-surface", here.id);
    document.body.setAttribute("data-cns-gear", here.gear);
    document.body.setAttribute("data-cns-type", here.cns);
    document.body.setAttribute("data-cns-depth", here.depth);
    document.body.setAttribute("data-cns-pages", here.pages);
  }

  /* ── Init ── */
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", stamp);
  } else {
    stamp();
  }

  /* ── Expose ── */
  window.CNS = {
    SURFACES,
    FEEDS,
    SHIFTS,
    TOPO,
    identify,
    currentGear,
    cnsType,
    connections,
    availableShifts,
    navigateTo,
    topoSort,
    whereAmI,
  };

})();
