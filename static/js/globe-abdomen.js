// globe-abdomen.js — ABDOMEN: The gut. Digestion. RSS intake → nutrient extraction.
// Villi fold IN. Brain folds OUT. Same topology. Klein surface.
(function(){
  'use strict';
  if(!window.G) return;
  var G = window.G;
  
  function drawAbdomen(ctx, t) {
    var cx=G.cx, cy=G.cy, R=G.R;
    ctx.save();
    // Intestinal folds — the villi
    var villiCount = 20;
    for(var i=0;i<villiCount;i++){
      var angle = (i/villiCount)*Math.PI*2;
      var r = R*0.18 + Math.sin(t*0.002+i*0.8)*R*0.02;
      var x = cx + Math.cos(angle)*r;
      var y = cy + R*0.15 + Math.sin(angle)*r*0.6;
      var h = R*0.03 + Math.sin(t*0.003+i)*R*0.01;
      ctx.strokeStyle = 'rgba(255,136,68,'+(0.08+Math.sin(t*0.001+i)*0.04)+')';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(x, y);
      ctx.lineTo(x + Math.cos(angle)*h, y + Math.sin(angle)*h*0.6);
      ctx.stroke();
    }
    // Stomach outline
    ctx.strokeStyle = 'rgba(255,136,68,0.08)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.ellipse(cx, cy+R*0.15, R*0.2, R*0.15, 0, 0, G.TAU);
    ctx.stroke();
    ctx.fillStyle = 'rgba(255,136,68,0.2)';
    ctx.font = '8px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('ABDOMEN', cx, cy + R*0.35);
    ctx.restore();
  }
  
  G.drawModules.push(drawAbdomen);
})();
