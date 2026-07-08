const EXERCISE_COLORS = {
  SQUAT: '#00D4FF',
  'BICEP CURL': '#9B59FF',
  'PUSH UP': '#FF2CF3',
  'SHOULDER PRESS': '#00D4FF',
  LUNGE: '#2DFF7A'
};

function gradeFromScore(score){
  if(score >= 90) return {grade:'A', color:'#00D4FF'};
  if(score >= 75) return {grade:'B', color:'#9B59FF'};
  if(score >= 60) return {grade:'C', color:'#FF2CF3'};
  return {grade:'D', color:'#FF3B3B'};
}

function glowStyle(color){
  return `0 0 18px ${color}55, 0 0 40px ${color}22`;
}

function renderBreakdown(){
  const breakdown = [
    {name:'SQUAT', pct: 74},
    {name:'BICEP CURL', pct: 63},
    {name:'PUSH UP', pct: 81},
    {name:'SHOULDER PRESS', pct: 57},
    {name:'LUNGE', pct: 68}
  ];

  const root = document.getElementById('breakdownBars');
  if(!root) return;
  root.innerHTML = '';

  breakdown.forEach(item => {
    const color = EXERCISE_COLORS[item.name] || '#9B59FF';

    const row = document.createElement('div');
    row.className = 'breakdown-row';

    row.innerHTML = `
      <div class="br-label neon-purple">${item.name}</div>
      <div class="br-track">
        <div class="br-fill" style="width:${item.pct}%; background:${color}; box-shadow:${glowStyle(color)}"></div>
      </div>
      <div class="br-pct">${item.pct}%</div>
    `;

    root.appendChild(row);
  });
}

function renderRecentTable(){
  const rows = [
    {date:'2026-06-11', ex:'SQUAT', reps: 22, avg: 88, best: 20, score: 88},
    {date:'2026-06-12', ex:'PUSH UP', reps: 30, avg: 76, best: 26, score: 76},
    {date:'2026-06-13', ex:'BICEP CURL', reps: 18, avg: 83, best: 16, score: 83},
    {date:'2026-06-14', ex:'LUNGE', reps: 20, avg: 72, best: 18, score: 72},
    {date:'2026-06-15', ex:'SHOULDER PRESS', reps: 16, avg: 91, best: 15, score: 91},
    {date:'2026-06-16', ex:'SQUAT', reps: 24, avg: 86, best: 22, score: 86}
  ];

  const tbody = document.getElementById('recentTableBody');
  if(!tbody) return;
  tbody.innerHTML = '';

  rows.forEach((r, idx) => {
    const g = gradeFromScore(r.score);
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${r.date}</td>
      <td>${r.ex}</td>
      <td>${r.reps}</td>
      <td>${r.avg}</td>
      <td>${r.best}</td>
      <td>
        <span class="grade-badge" style="border-color:${g.color}55; color:${g.color}; box-shadow:${glowStyle(g.color)}">${g.grade}</span>
      </td>
    `;
    tr.style.animationDelay = `${idx * 60}ms`;
    tbody.appendChild(tr);
  });
}

function renderPersonalBests(){
  const bests = [
    {title:'BEST FORM SCORE', value:'98/100', color:'#FFB000'},
    {title:'BEST REP COUNT', value:'42 REPS', color:'#00D4FF'},
    {title:'LONGEST STREAK', value:'9 DAYS', color:'#FF2CF3'}
  ];

  const root = document.getElementById('pbsRow');
  if(!root) return;
  root.innerHTML = '';

  bests.forEach((b) => {
    const card = document.createElement('div');
    card.className = 'pbst-card card borderGlow';
    card.style.borderTop = `2px solid ${b.color}`;
    card.innerHTML = `
      <div class="pbst-trophy" style="color:${b.color}; text-shadow:0 0 16px ${b.color}aa">🏆</div>
      <div class="pbst-title neon-purple">${b.title}</div>
      <div class="pbst-value neon-h neon-h--3d" style="color:${b.color};">${b.value}</div>
    `;
    root.appendChild(card);
  });
}

function initCharts(){
  const lineEl = document.getElementById('lineChart');
  const barEl = document.getElementById('barChart');
  if(!lineEl || !barEl) return;

  const labels = ['S1','S2','S3','S4','S5','S6','S7'];
  const formScores = [72, 81, 79, 88, 90, 95, 86];
  const reps = [24, 31, 28, 35, 30, 40, 33];

  const gridColor = 'rgba(155,89,255,0.25)';
  const cyan = '#00D4FF';
  const purple = '#9B59FF';

  new Chart(lineEl, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'Form Score',
        data: formScores,
        borderColor: cyan,
        backgroundColor: 'rgba(0,212,255,0.08)',
        tension: 0.35,
        pointRadius: 4,
        pointHoverRadius: 6,
        pointBackgroundColor: cyan,
        pointBorderWidth: 0,
        borderWidth: 2,
        fill: true
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { color: 'transparent' }, ticks: { display: false } },
        y: { grid: { color: gridColor }, ticks: { display: false }, min: 0, max: 100 }
      }
    }
  });

  new Chart(barEl, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Reps',
        data: reps,
        backgroundColor: purple,
        borderColor: 'rgba(155,89,255,.9)',
        borderWidth: 0,
        hoverBackgroundColor: '#00D4FF'
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false }, ticks: { display: false } },
        y: { grid: { color: 'rgba(0,212,255,0.15)' }, ticks: { display: false } }
      }
    }
  });
}

window.addEventListener('DOMContentLoaded', () => {
  renderBreakdown();
  renderRecentTable();
  renderPersonalBests();
  initCharts();
});

