/* reality-map.js — reality overlay.
 * Maps the membrane onto physical reality. Uses PiOrient landmarks
 * and Stadial geological time as the reality substrate.
 * The HUD is a lens. Reality is underneath. */
(function(){
  "use strict";
  function realityLayer() {
    var layers = {};
    if (window.PiOrient) layers.orientation = window.PiOrient.orient("detroit");
    if (window.Stadial) layers.time = { period: window.Stadial.periodAt(0), rhythm: window.Stadial.rhythm().length };
    if (window.MobiusViewport) layers.viewport = { aspect: window.MobiusViewport.VP.aspect, nullFrac: window.MobiusViewport.nullZone().fraction };
    if (window.CNS) layers.position = window.CNS.whereAmI();
    return layers;
  }
  window.RealityMap = { realityLayer: realityLayer };
})();
