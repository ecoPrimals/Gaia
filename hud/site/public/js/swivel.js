/* swivel.js — viewport swivel.
 * Rotates the observation angle. Works with MobiusViewport. */
(function(){
  "use strict";
  var angle = 0;
  function swivel(deg) { angle = (angle + deg) % 360; document.body.style.setProperty("--swivel-angle", angle + "deg"); }
  function reset() { angle = 0; document.body.style.setProperty("--swivel-angle", "0deg"); }
  function current() { return angle; }
  window.Swivel = { swivel: swivel, reset: reset, current: current };
})();
