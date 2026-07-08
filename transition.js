(() => {
  const prefersReduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const root = document.querySelector('.page');
  if (!root) return;
  if (prefersReduced) { root.classList.add('is-visible'); return; }

  // Force fade-in
  requestAnimationFrame(() => {
    root.classList.add('is-visible');
  });
})();

