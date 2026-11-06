/* twist-jump.js — möbius twist discontinuity.
 * When you cross a boundary, the twist inverts. The jump is the phase shift.
 * Handles the half-twist in the möbius strip — what flips when you wrap. */
(function(){
  "use strict";
  var flipped = false;
  function twist() { flipped = !flipped; document.body.classList.toggle("mobius-flipped", flipped); return flipped; }
  function isFlipped() { return flipped; }
  function jump(from, to) {
    if (window.CNS) {
      var shift = window.CNS.availableShifts();
      if (shift.length > 0) twist();
    }
    return flipped;
  }
  window.TwistJump = { twist: twist, isFlipped: isFlipped, jump: jump };
})();
