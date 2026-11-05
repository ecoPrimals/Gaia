/**
 * synapse.js — the interaction layer. The snow globe.
 * Gold wisps reach toward the cursor. The organism breathes with scroll.
 * She FEELS the visitor. The visitor FEELS her.
 */
(function synapse() {
  const canvas = document.createElement('canvas');
  canvas.id = 'synapse-layer';
  canvas.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:9999;opacity:0.6';
  document.body.appendChild(canvas);
  const ctx = canvas.getContext('2d');
  let W, H, mx = -1, my = -1, scrollY = 0, breath = 0, particles = [];
  const GOLD = [255, 215, 0];
  const GREEN = [90, 184, 122];
  const MAX_P = 60;

  function resize() { W = canvas.width = window.innerWidth; H = canvas.height = window.innerHeight; }
  resize(); window.addEventListener('resize', resize);

  document.addEventListener('mousemove', e => { mx = e.clientX; my = e.clientY; });
  document.addEventListener('mouseleave', () => { mx = -1; my = -1; });
  window.addEventListener('scroll', () => { scrollY = window.scrollY; });

  function spawn(x, y, color, life) {
    if (particles.length >= MAX_P) return;
    const angle = Math.random() * Math.PI * 2;
    const speed = 0.3 + Math.random() * 1.2;
    particles.push({
      x, y, vx: Math.cos(angle) * speed, vy: Math.sin(angle) * speed,
      r: color[0], g: color[1], b: color[2],
      life: life || 80 + Math.random() * 60, maxLife: life || 80 + Math.random() * 60,
      size: 1.5 + Math.random() * 2.5,
    });
  }

  function draw() {
    ctx.clearRect(0, 0, W, H);
    breath += 0.02;
    const breathAmp = Math.sin(breath) * 0.3 + 0.7;

    // Gold wisps reach toward cursor
    if (mx > 0 && my > 0) {
      for (let i = 0; i < 2; i++) {
        const cx = W / 2 + (Math.random() - 0.5) * W * 0.6;
        const cy = H / 2 + (Math.random() - 0.5) * H * 0.6;
        const dx = mx - cx, dy = my - cy;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 300) {
          const nx = cx + dx * 0.3 + (Math.random() - 0.5) * 20;
          const ny = cy + dy * 0.3 + (Math.random() - 0.5) * 20;
          spawn(nx, ny, GOLD, 40 + Math.random() * 30);
        }
      }
    }

    // Breathing particles — scroll-responsive
    if (Math.random() < 0.15) {
      const x = W / 2 + (Math.random() - 0.5) * 100;
      const y = H / 2 + Math.sin(breath * 2) * 30 + (Math.random() - 0.5) * 40;
      spawn(x, y, GREEN, 60);
    }

    // Update + draw particles
    for (let i = particles.length - 1; i >= 0; i--) {
      const p = particles[i];
      p.x += p.vx; p.y += p.vy;
      p.life--;

      // Gravity toward center (the organism pulls)
      const dx = W / 2 - p.x, dy = H / 2 - p.y;
      const dist = Math.sqrt(dx * dx + dy * dy) + 1;
      p.vx += dx / dist * 0.01;
      p.vy += dy / dist * 0.01;

      // Damping
      p.vx *= 0.99; p.vy *= 0.99;

      if (p.life <= 0) { particles.splice(i, 1); continue; }

      const alpha = (p.life / p.maxLife) * breathAmp * 0.5;
      const sz = p.size * (p.life / p.maxLife);
      ctx.beginPath();
      ctx.arc(p.x, p.y, sz, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${p.r},${p.g},${p.b},${alpha})`;
      ctx.fill();

      // Glow
      if (alpha > 0.2) {
        ctx.beginPath();
        ctx.arc(p.x, p.y, sz * 2.5, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${p.r},${p.g},${p.b},${alpha * 0.15})`;
        ctx.fill();
      }
    }

    // Center heartbeat glow
    const hb = Math.sin(breath * 3) * 0.15 + 0.15;
    ctx.beginPath();
    ctx.arc(W / 2, H / 2, 20 + Math.sin(breath * 3) * 8, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(90,184,122,${hb})`;
    ctx.fill();

    requestAnimationFrame(draw);
  }
  draw();

  console.log('%c✨ synapse.js — interaction layer ALIVE. Gold wisps reach for you.',
    'color:#ffd700;font-weight:bold');
})();
