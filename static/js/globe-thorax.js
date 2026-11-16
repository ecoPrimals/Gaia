// globe-thorax.js — RIBS/THORAX: The protective cage. BarraCuda ribs.
// Ribs protect the heart (pulse) and lungs (breath).
(function(){
  'use strict';
  if(!window.G) return;
  var G = window.G;
  
  function drawThorax(ctx, t) {
    var cx=G.cx, cy=G.cy, R=G.R;
    ctx.save();
    // 12 rib pairs — curved arcs
    var ribCount = 12;
    for(var i=0;i<ribCount;i++){
      var y = cy - R*0.25 + (i/ribCount)*R*0.55;
      var w = R*0.4 * (1 - Math.abs(i/ribCount - 0.4)*1.5);
      if(w < R*0.05) w = R*0.05;
      var breathe = Math.sin(t*0.002 + i*0.3)*R*0.008;
      ctx.strokeStyle = 'rgba(255,68,68,'+(0.06+i*0.005)+')';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.ellipse(cx, y+breathe, w, R*0.02, 0, 0, Math.PI);
      ctx.stroke();
      // Mirror
      ctx.beginPath();
      ctx.ellipse(cx, y+breathe, w, R*0.02, 0, Math.PI, G.TAU);
      ctx.stroke();
    }
    // Sternum — central bone
    ctx.strokeStyle = 'rgba(255,68,68,0.12)';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(cx, cy - R*0.25);
    ctx.lineTo(cx, cy + R*0.2);
    ctx.stroke();
    ctx.fillStyle = 'rgba(255,68,68,0.2)';
    ctx.font = '8px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('THORAX', cx, cy + R*0.28);
    ctx.restore();
  }
  
  G.drawModules.push(drawThorax);
})();
