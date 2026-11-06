/* deep-view.js — depth navigation overlay.
 * Visual layer for PoreDepth bag-of-holding navigation.
 * Shows current depth level, available pores, navigable paths. */
(function(){
  "use strict";
  function depthIndicator() {
    if (!window.PoreDepth) return null;
    var scan = window.PoreDepth.scan();
    return { deepest: scan.deepest, maxDepth: scan.maxDepth, poreCount: scan.poreCount, bagPages: scan.bagPages };
  }
  window.DeepView = { depthIndicator: depthIndicator };
})();
