/* horizon.js — horizon line.
 * The horizon is where the membrane meets the null exhaust.
 * At eye level: horizon = sqrt(2Rh) where R=Earth radius, h=observer height. */
(function(){
  "use strict";
  var R_KM = 6371;
  function horizonKm(h_m) { return Math.sqrt(2 * R_KM * (h_m / 1000)); }
  function horizonPx() {
    var vp = window.MobiusViewport;
    return vp ? vp.VP.cy + vp.VP.R * 0.1 : window.innerHeight * 0.55;
  }
  document.addEventListener("DOMContentLoaded", function() {
    document.body.style.setProperty("--horizon-y", horizonPx() + "px");
  });
  window.Horizon = { horizonKm: horizonKm, horizonPx: horizonPx };
})();
