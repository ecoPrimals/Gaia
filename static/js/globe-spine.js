// globe-spine.js — SPINE: The backbone. 48 shell scripts. Quicksilver/RSS.
// Vertebrae = cron jobs. Spinal cord = data flow. Each vertebra is a beat.
(function(){
  'use strict';
  if(!window.G) return;
  var G = window.G;
  
  function drawSpine(ctx, t) {
    var cx=G.cx, cy=G.cy, R=G.R;
    ctx.save();
    // 24 vertebrae down the center
    var vertebrae = 24;
    for(var i=0;i<vertebrae;i++){
      var y = cy - R*0.5 + (i/vertebrae)*R*1.0;
      var pulse = Math.sin(t*0.004 + i*0.5)*0.3 + 0.7;
      var w = R*0.03 + Math.sin(i*0.6)*R*0.01;
      // Vertebral body
      ctx.fillStyle = 'rgba(255,220,100,'+pulse*0.06+')';
      ctx.fillRect(cx-w, y-R*0.008, w*2, R*0.016);
      // Spinous process
      ctx.strokeStyle = 'rgba(255,220,100,'+pulse*0.04+')';
      ctx.lineWidth = 0.5;
      ctx.beginPath();
      ctx.moveTo(cx-w*1.5, y);
      ctx.lineTo(cx+w*1.5, y);
      ctx.stroke();
      // Nerve root
      if(i%3===0){
        ctx.strokeStyle = 'rgba(255,220,100,0.03)';
        ctx.beginPath();
        ctx.moveTo(cx-w, y);
        ctx.lineTo(cx-R*0.25, y+R*0.02);
        ctx.moveTo(cx+w, y);
        ctx.lineTo(cx+R*0.25, y+R*0.02);
        ctx.stroke();
      }
    }
    // Spinal cord — central line
    ctx.strokeStyle = 'rgba(255,220,100,0.12)';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(cx, cy-R*0.5);
    ctx.lineTo(cx, cy+R*0.5);
    ctx.stroke();
    ctx.fillStyle = 'rgba(255,220,100,0.2)';
    ctx.font = '8px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('SPINE (48 scripts)', cx+R*0.3, cy);
    ctx.restore();
  }
  
  G.drawModules.push(drawSpine);
})();
