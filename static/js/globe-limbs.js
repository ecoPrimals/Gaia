// globe-limbs.js — LIMBS/FINGERS: The extremities. FINGERS = JS.
// Hands touch the world. API handlers ARE the fingers.
(function(){
  'use strict';
  if(!window.G) return;
  var G = window.G;
  
  function drawLimbs(ctx, t) {
    var cx=G.cx, cy=G.cy, R=G.R;
    ctx.save();
    // Four limbs — arms and legs
    var limbs = [
      {ox:-0.4,oy:-0.1,dx:-0.6,dy:0.2, label:'L.ARM'},
      {ox:0.4,oy:-0.1,dx:0.6,dy:0.2, label:'R.ARM'},
      {ox:-0.15,oy:0.35,dx:-0.25,dy:0.65, label:'L.LEG'},
      {ox:0.15,oy:0.35,dx:0.25,dy:0.65, label:'R.LEG'},
    ];
    limbs.forEach(function(l,i){
      var sway = Math.sin(t*0.002+i*1.5)*R*0.01;
      ctx.strokeStyle = 'rgba(100,255,100,0.1)';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(cx+l.ox*R, cy+l.oy*R);
      ctx.lineTo(cx+l.dx*R+sway, cy+l.dy*R);
      ctx.stroke();
      // Fingers at end of arms
      if(i < 2){
        for(var f=0;f<5;f++){
          var angle = (f-2)*0.15 + (i===0?Math.PI:0);
          var fx = cx+l.dx*R+sway + Math.cos(angle)*R*0.04;
          var fy = cy+l.dy*R + Math.sin(angle)*R*0.04;
          ctx.strokeStyle = 'rgba(100,255,100,0.06)';
          ctx.lineWidth = 0.5;
          ctx.beginPath();
          ctx.moveTo(cx+l.dx*R+sway, cy+l.dy*R);
          ctx.lineTo(fx, fy);
          ctx.stroke();
        }
      }
    });
    ctx.fillStyle = 'rgba(100,255,100,0.15)';
    ctx.font = '8px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('FINGERS=JS', cx, cy + R*0.72);
    ctx.restore();
  }
  
  G.drawModules.push(drawLimbs);
})();
