
(() => {
  const prefersReduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (prefersReduced) return;

  const mount = document.getElementById('particleMount');
  if (!mount) return;

  const canvas = document.createElement('canvas');
  canvas.id = 'particleCanvas';
  canvas.style.position = 'absolute';
  canvas.style.inset = '0';
  canvas.style.width = '100%';
  canvas.style.height = '100%';
  canvas.style.pointerEvents = 'none';
  mount.appendChild(canvas);

  const ctx = canvas.getContext('2d');

  const DPR = Math.min(2, window.devicePixelRatio || 1);

  let w = 0, h = 0;
  function resize(){
    const rect = mount.getBoundingClientRect();
    w = Math.max(1, rect.width);
    h = Math.max(1, rect.height);
    canvas.width = Math.floor(w * DPR);
    canvas.height = Math.floor(h * DPR);
    ctx.setTransform(DPR,0,0,DPR,0,0);
  }
  window.addEventListener('resize', resize);
  resize();

  const BLUE = [0, 212, 255];
  const PURPLE = [155, 89, 255];

  const COUNT = Math.round(Math.min(120, Math.max(55, (w*h)/18000)));
  const dots = [];

  function rand(min, max){return Math.random()*(max-min)+min;}

  for(let i=0;i<COUNT;i++){
    const isBlue = Math.random() > 0.35;
    dots.push({
      x: rand(0,w),
      y: rand(0,h),
      vx: rand(-0.25, 0.25),
      vy: rand(-0.18, 0.18),
      r: rand(1.2, 2.2),
      c: isBlue ? BLUE : PURPLE,
      a: rand(0.3, 0.9)
    });
  }

  const LINK_DIST = 105;

  function drawDot(d){
    ctx.beginPath();
    ctx.arc(d.x,d.y,d.r,0,Math.PI*2);
    ctx.fillStyle = `rgba(${d.c[0]},${d.c[1]},${d.c[2]},${d.a})`;
    ctx.shadowColor = `rgba(${d.c[0]},${d.c[1]},${d.c[2]},0.8)`;
    ctx.shadowBlur = 12;
    ctx.fill();
    ctx.shadowBlur = 0;
  }

  function drawLine(a,b,alpha){
    ctx.beginPath();
    ctx.moveTo(a.x,a.y);
    ctx.lineTo(b.x,b.y);
    ctx.strokeStyle = `rgba(0,212,255,${alpha})`;
    ctx.shadowColor = 'rgba(0,212,255,0.65)';
    ctx.shadowBlur = 14;
    ctx.lineWidth = 1;
    ctx.stroke();
    ctx.shadowBlur = 0;
  }

  let tPrev = performance.now();
  function tick(t){
    const dt = Math.min(32, t - tPrev);
    tPrev = t;

    ctx.clearRect(0,0,w,h);

    // Update positions
    for(const d of dots){
      d.x += d.vx * (dt/16);
      d.y += d.vy * (dt/16);

      if(d.x < -10) d.x = w+10;
      if(d.x > w+10) d.x = -10;
      if(d.y < -10) d.y = h+10;
      if(d.y > h+10) d.y = -10;
    }

    // Lines
    for(let i=0;i<dots.length;i++){
      const a = dots[i];
      for(let j=i+1;j<dots.length;j++){
        const b = dots[j];
        const dx = a.x - b.x;
        const dy = a.y - b.y;
        const dist = Math.sqrt(dx*dx + dy*dy);
        if(dist < LINK_DIST){
          const alpha = (1 - dist/LINK_DIST) * 0.38;
          if(alpha > 0.02) drawLine(a,b,alpha);
        }
      }
    }

    // Dots
    for(const d of dots) drawDot(d);

    requestAnimationFrame(tick);
  }

  requestAnimationFrame(tick);
})();

