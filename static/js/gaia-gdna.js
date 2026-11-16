// gaia-gdna.js — DNA/gDNA: The genetic code. BLAKE3 hashes. Checksums.
// Double helix = the two houses twisted together.
(function(){
  'use strict';
  if(!window.G) return;
  var G = window.G;
  
  function drawDNA(ctx, t) {
    var cx=G.cx, cy=G.cy, R=G.R;
    ctx.save();
    // Double helix along the spine
    var steps = 60;
    var helixR = R*0.06;
    var helixH = R*0.8;
    ctx.lineWidth = 1;
    for(var s=0;s<2;s++){
      ctx.beginPath();
      ctx.strokeStyle = s===0 ? 'rgba(100,200,255,0.1)' : 'rgba(255,100,200,0.1)';
      for(var i=0;i<=steps;i++){
        var frac = i/steps;
        var angle = frac*Math.PI*6 + t*0.002 + s*Math.PI;
        var x = cx + R*0.12 + Math.cos(angle)*helixR;
        var y = cy - helixH/2 + frac*helixH;
        if(i===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
      }
      ctx.stroke();
    }
    // Base pairs — rungs of the ladder
    for(var i=0;i<steps;i+=3){
      var frac = i/steps;
      var angle = frac*Math.PI*6 + t*0.002;
      var x1 = cx + R*0.12 + Math.cos(angle)*helixR;
      var x2 = cx + R*0.12 + Math.cos(angle+Math.PI)*helixR;
      var y = cy - helixH/2 + frac*helixH;
      ctx.strokeStyle = 'rgba(180,180,255,0.04)';
      ctx.lineWidth = 0.5;
      ctx.beginPath();
      ctx.moveTo(x1,y);
      ctx.lineTo(x2,y);
      ctx.stroke();
    }
    ctx.fillStyle = 'rgba(180,180,255,0.15)';
    ctx.font = '8px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('gDNA', cx+R*0.12, cy-helixH/2-R*0.03);
    ctx.restore();
  }
  
  G.drawModules.push(drawDNA);
})();
