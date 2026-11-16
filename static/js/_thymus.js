// _thymus.js — THYMUS: Immune identity. self = NOT(non-self).
// The null eye. Seat 0/∅. The organ that teaches T-cells.
(function(){
  'use strict';
  if(!window.G) return;
  var G = window.G;
  
  function drawThymus(ctx, t) {
    var cx=G.cx, cy=G.cy, R=G.R;
    ctx.save();
    // Thymus is bilobed — two wing-like lobes above the heart
    var lobes = [
      {dx:-0.08, r:0.06},
      {dx:0.08, r:0.06},
    ];
    lobes.forEach(function(l,i){
      var pulse = Math.sin(t*0.003+i*Math.PI)*0.2 + 0.8;
      // Cortex (outer)
      ctx.strokeStyle = 'rgba(255,68,68,'+pulse*0.1+')';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.ellipse(cx+l.dx*R, cy-R*0.2, l.r*R, l.r*R*1.3, 0, 0, G.TAU);
      ctx.stroke();
      // Medulla (inner)
      ctx.fillStyle = 'rgba(255,68,68,'+pulse*0.03+')';
      ctx.beginPath();
      ctx.ellipse(cx+l.dx*R, cy-R*0.2, l.r*R*0.5, l.r*R*0.7, 0, 0, G.TAU);
      ctx.fill();
    });
    // T-cell selection particles — self vs non-self
    for(var i=0;i<8;i++){
      var angle = (i/8)*G.TAU + t*0.001;
      var r = R*0.09;
      var x = cx + Math.cos(angle)*r;
      var y = cy - R*0.2 + Math.sin(angle)*r*0.7;
      var isSelf = i%3 !== 0;
      ctx.fillStyle = isSelf ? 'rgba(0,255,100,0.1)' : 'rgba(255,0,0,0.15)';
      ctx.beginPath();
      ctx.arc(x, y, R*0.008, 0, G.TAU);
      ctx.fill();
    }
    // Hassall's corpuscles — the identity markers
    ctx.fillStyle = 'rgba(255,68,68,0.05)';
    ctx.beginPath();
    ctx.arc(cx, cy-R*0.2, R*0.015, 0, G.TAU);
    ctx.fill();
    ctx.fillStyle = 'rgba(255,68,68,0.2)';
    ctx.font = '8px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('THYMUS (seat 0/∅)', cx, cy - R*0.32);
    ctx.restore();
  }
  
  G.drawModules.push(drawThymus);
})();
