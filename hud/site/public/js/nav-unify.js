/* nav-unify.js — unified navigation.
 * Uses CNS router for cross-surface navigation with depth guards. */
(function(){
  "use strict";
  function go(surfaceId, opts) {
    if (window.CNS) return window.CNS.navigateTo(surfaceId, opts || {});
    var domains = { detroit:"detroit.primals.eco", clutch:"clutch.primals.eco", sporeprint:"sporeprint.primals.eco",
      tuebor:"tuebor.primals.eco", signal:"signal.primals.eco", hud:"hud.primals.eco", water:"water.primals.eco",
      gorilla:"gorilla.primals.eco", barry:"barry.primals.eco", hypothesis:"hypothesis.primals.eco" };
    if (domains[surfaceId]) location.href = "https://" + domains[surfaceId] + (opts && opts.path || "/");
    return { navigating: true };
  }
  window.NavUnify = { go: go };
})();
