/* synesthesia.js — cross-modal perception.
 * Maps between pores: sound→color, shape→frequency, data→texture.
 * The membrane is synesthetic — every pore can feel every other pore. */
(function(){
  "use strict";
  var PORE_HZ = { visual:440, audio:261.6, tactile:174.6, pointer:329.6, symbolic:392, spatial:349.2, data:523.3, persistence:293.7 };
  function poreToColor(pore) {
    var hz = PORE_HZ[pore] || 440;
    var hue = ((hz - 174.6) / (523.3 - 174.6)) * 360;
    return "hsl(" + hue + ",60%,50%)";
  }
  function dataToTone(value, min, max) {
    var t = (value - min) / (max - min);
    return 174.6 + t * (523.3 - 174.6);
  }
  window.Synesthesia = { PORE_HZ: PORE_HZ, poreToColor: poreToColor, dataToTone: dataToTone };
})();
