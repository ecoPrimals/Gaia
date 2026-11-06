/* orbit.js — solar orbital orientation.
 * Celestial mechanics for the HUD.  Delegates to Stadial + PiOrient.
 * Stub — awaiting full orbital model. */
(function(){
  "use strict";
  var PI = Math.PI;
  // Earth orbital period in seconds
  var YEAR_S = 365.25 * 24 * 3600;
  // Current position in orbit (fraction of year, 0=vernal equinox)
  function orbitalPhase() {
    var now = new Date();
    var equinox = new Date(now.getFullYear(), 2, 20); // ~March 20
    var diff = (now - equinox) / 1000;
    if (diff < 0) diff += YEAR_S;
    return diff / YEAR_S;
  }
  // Solar hour angle at observer longitude
  function solarAngle(lonDeg) {
    var now = new Date();
    var utcHours = now.getUTCHours() + now.getUTCMinutes()/60;
    var solarNoon = 12 - (lonDeg / 15);
    var hourAngle = (utcHours - solarNoon) * 15;
    return hourAngle;
  }
  // Expose
  window.Orbit = { orbitalPhase: orbitalPhase, solarAngle: solarAngle, YEAR_S: YEAR_S };
})();
