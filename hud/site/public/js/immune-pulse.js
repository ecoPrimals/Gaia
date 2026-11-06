/* immune-pulse.js — immune system heartbeat.
 * Visualizes the scatter/honeycomb defense pulse.
 * Reads opsonize-rs negentropy output. */
(function(){
  "use strict";
  var lastPulse = Date.now();
  function pulse() {
    var now = Date.now();
    var interval = now - lastPulse;
    lastPulse = now;
    return { interval_ms: interval, bpm: 60000 / interval };
  }
  function isHealthy() { return (Date.now() - lastPulse) < 30000; }
  window.ImmunePulse = { pulse: pulse, isHealthy: isHealthy };
})();
