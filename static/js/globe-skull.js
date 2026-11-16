// globe-skull.js — SKULL: The thinking layer. JS IS the skull.
// Cranium = the protective case around computation.
// 26 body parts identified. Skull holds the brain.
(function(){
  'use strict';
  if(!window.G) return;
  var G = window.G;
  
  function drawSkull(ctx, t) {
    var cx=G.cx, cy=G.cy, R=G.R;
    // Cranial vault — elliptical dome above center
    ctx.save();
    ctx.strokeStyle = 'rgba(255,204,100,0.15)';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.ellipse(cx, cy - R*0.15, R*0.35, R*0.45, 0, Math.PI, 0);
    ctx.stroke();
    // Suture lines — the cranial seams
    var sutures = [
      {x1:-0.15,y1:-0.55,x2:0.15,y2:-0.55}, // coronal
      {x1:0,y1:-0.6,x2:0,y2:-0.35},           // sagittal
      {x1:-0.1,y1:-0.35,x2:0.1,y2:-0.35},     // lambdoid
    ];
    ctx.strokeStyle = 'rgba(255,204,100,0.08)';
    ctx.lineWidth = 0.5;
    sutures.forEach(function(s){
      ctx.beginPath();
      ctx.moveTo(cx+s.x1*R, cy+s.y1*R);
      ctx.lineTo(cx+s.x2*R, cy+s.y2*R);
      ctx.stroke();
    });
    // Fontanelle pulse — the soft spot
    var pulse = Math.sin(t*0.003)*0.3 + 0.7;
    ctx.fillStyle = 'rgba(255,204,100,'+pulse*0.05+')';
    ctx.beginPath();
    ctx.arc(cx, cy-R*0.5, R*0.04, 0, G.TAU);
    ctx.fill();
    // Label
    ctx.fillStyle = 'rgba(255,204,100,0.3)';
    ctx.font = '9px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('SKULL', cx, cy-R*0.6);
    ctx.restore();
  }
  
  G.drawModules.push(drawSkull);
})();
