// Global app helpers: navbar scroll, reveal on load, smooth counters

function setupNavbarScroll(){
  const nav = document.getElementById('siteNavbar');
  if(!nav) return;
  const onScroll = () => {
    const scrolled = window.scrollY > 10;
    nav.classList.toggle('navbar--scrolled', scrolled);
  };
  onScroll();
  window.addEventListener('scroll', onScroll, {passive:true});
}

function setupReveal(){
  const nodes = Array.from(document.querySelectorAll('[data-reveal]'));
  const applyVisible = (el) => el.classList.add('is-visible');

  const io = new IntersectionObserver((entries) => {
    for(const e of entries){
      if(e.isIntersecting) applyVisible(e.target);
    }
  }, {threshold: 0.15});

  nodes.forEach((el, idx) => {
    el.style.transitionDelay = `${Math.min(450, idx * 80)}ms`;
    io.observe(el);
  });
}

function setupCountUp(){
  const counters = Array.from(document.querySelectorAll('[data-count]'));
  const fmt = (n) => String(n);

  const io = new IntersectionObserver((entries) => {
    for(const e of entries){
      if(!e.isIntersecting) continue;
      const el = e.target;
      const target = parseInt(el.getAttribute('data-count') || '0', 10);
      const start = 0;
      const duration = 1200;
      const t0 = performance.now();

      const tick = (t) => {
        const p = Math.min(1, (t - t0) / duration);
        const v = Math.round(start + (target - start) * (p));
        el.textContent = fmt(v);
        if(p < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
      io.unobserve(el);
    }
  }, {threshold: 0.35});

  counters.forEach(el => io.observe(el));
}

// If CSS ring exists, update based on score
function updateFormRing(score){
  const ringFg = document.querySelector('.ring-fg');
  if(!ringFg) return;
  const radius = parseFloat(ringFg.getAttribute('r') || '48');
  const c = 2 * Math.PI * radius;
  const clamped = Math.max(0, Math.min(100, score));
  const offset = c * (1 - clamped/100);
  ringFg.style.strokeDashoffset = String(offset);
}

// Boot
window.addEventListener('DOMContentLoaded', () => {
  setupNavbarScroll();
  setupReveal();
  setupCountUp();

  // Optional: allow page demos to call updateFormRing
  window.__updateFormRing = updateFormRing;
});

