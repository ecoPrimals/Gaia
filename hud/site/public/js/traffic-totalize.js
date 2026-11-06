/* traffic-totalize.js — traffic aggregation.
 * Totalizes fleet and human traffic from membrane feeds. */
(function(){
  "use strict";
  function totals() {
    var dash = document.querySelector("[data-dashboard]");
    if (dash) {
      try { return JSON.parse(dash.getAttribute("data-dashboard")); } catch(e){}
    }
    return { humans: 0, fleet: 0, ratio: 0 };
  }
  window.TrafficTotalize = { totals: totals };
})();
