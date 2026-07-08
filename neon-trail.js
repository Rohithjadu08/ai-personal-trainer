(function(){
  const TRAIL_COUNT = 14;
  const GAP = 0.18;
  const cyan = 'rgba(0,212,255,0.55)';
  const cyanGlow = '0 0 14px rgba(0,212,255,0.75)';

  let enabled = true;
  const prefersReduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if(prefersReduced) enabled = false;

  if(!enabled) return;

  let pointer = {x: window.innerWidth/2, y: window.innerHeight/2};
  let last = {...pointer};

  const root = document.createElement('div');
  root.className = 'cursor-trail';
  document.body.appendChild(root);

  const dots = [];
  for(let i=0;i<TRAIL_COUNT;i++){
    const el = document.createElement('i');
    el.style.opacity = String((TRAIL_COUNT - i)/TRAIL_COUNT);
    el.style.filter = `saturate(${1.2 - i*0.03})`;
    root.appendChild(el);
    dots.push(el);
  }

  window.addEventListener('mousemove', (e)=>{
    pointer.x = e.clientX;
    pointer.y = e.clientY;
  }, {passive:true});

  function animate(){
    last.x += (pointer.x - last.x) * GAP;
    last.y += (pointer.y - last.y) * GAP;

    let curX = last.x;
    let curY = last.y;

    for(let i=0;i<dots.length;i++){
      const t = (i+1)/dots.length;
      const dx = (pointer.x - curX) * t;
      const dy = (pointer.y - curY) * t;
      curX += dx*0.55;
      curY += dy*0.55;

      const dot = dots[i];
      dot.style.left = `${curX}px`;
      dot.style.top  = `${curY}px`;
      dot.style.background = cyan;
      dot.style.boxShadow = cyanGlow;
      dot.style.transform = `translate(-50%,-50%) scale(${1 - t*0.35})`;
    }

    requestAnimationFrame(animate);
  }

  requestAnimationFrame(animate);
})();

