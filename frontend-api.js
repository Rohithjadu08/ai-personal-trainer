(() => {
  const API = {
    base: window.fitaiApiBase(),
    async register(email = 'demo@local', password = 'password', name = 'Demo User'){
      try{
        const res = await fetch(`${this.base}/register`, {
          method: 'POST', headers: {'Content-Type':'application/json'},
          body: JSON.stringify({email, password, name})
        });
        if(res.status === 409) return null; // already exists
        return await res.json();
      }catch(e){ console.warn('register error', e); return null }
    },
    async login(email='demo@local', password='password'){
      try{
        const res = await fetch(`${this.base}/login`,{
          method:'POST', headers:{'Content-Type':'application/json'},
          body: JSON.stringify({email, password})
        });
        if(!res.ok) return null;
        return await res.json();
      }catch(e){ console.warn('login error', e); return null }
    }
  };

  async function initWorkout() {
    const email = 'demo@local';
    const password = 'password';

    // Try register (ignore if already exists)
    await API.register(email, password, 'Demo User');
    const auth = await API.login(email, password);
    if(!auth){ console.warn('Could not login to backend'); return }

    // backend register returned id on /register, but login returns token only.
    // The in-memory backend uses numeric user ids; try to decode token to get `sub`.
    let userId = null;
    try{
      const parts = auth.access_token.split('.');
      if(parts.length===3){
        const payload = JSON.parse(atob(parts[1].replace(/-/g,'+').replace(/_/g,'/')));
        userId = payload.sub;
      }
    }catch(e){ console.warn('decode token failed', e) }

    if(!userId){
      // fallback: use '1'
      userId = '1';
    }

    // connect websocket
    const ws = new WebSocket(`${window.fitaiWsBase()}/ws/${userId}`);
    ws.addEventListener('open', () => console.log('ws open'));
    ws.addEventListener('message', (ev) => {
      try{
        const data = JSON.parse(ev.data);
        // map to UI if present
        const rep = data.rep_count ?? data.reps ?? 0;
        const score = Math.round((data.form_score ?? data.form ?? 0) * 100) || 0;
        const stage = data.stage ?? '';
        const feedback = (data.feedback && data.feedback.length) ? data.feedback.join(' ') : (data.reply || '');

        const repEl = document.getElementById('repValue');
        const scoreEl = document.getElementById('formScore');
        const stageEl = document.getElementById('stageText');
        const fbEl = document.getElementById('feedbackText');

        if(repEl) repEl.textContent = String(rep);
        if(scoreEl) scoreEl.textContent = String(score);
        if(stageEl) stageEl.textContent = stage ? `STAGE: ${stage.toUpperCase()}` : stageEl.textContent;
        if(fbEl) fbEl.textContent = feedback;
        if(window.__updateFormRing) window.__updateFormRing(score);
      }catch(e){ console.warn('ws parse', e) }
    });
    ws.addEventListener('close', ()=> console.log('ws closed'));
    ws.addEventListener('error', (e)=> console.warn('ws error', e));
  }

  // Auto-init when train page loads
  window.addEventListener('DOMContentLoaded', () => {
    if(location.pathname.endsWith('train.html')){
      initWorkout().catch(e=>console.warn(e));
    }
  });

})();
