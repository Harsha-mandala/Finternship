/* ═══════════════════════════════════════════════════════════
   app.js — Navigation + App Init + API Status
   ═══════════════════════════════════════════════════════════ */

// ── Screen registry ───────────────────────────────────────────────────────────
const SCREENS = {
  dashboard:       renderDashboard,
  recommendations: renderRecommendations,
  'log-sales':     renderLogSales,
  trends:          renderTrends,
};

let _activeScreen = null;

// ── Navigation ────────────────────────────────────────────────────────────────
function navigateTo(screenId) {
  if (_activeScreen === screenId) return;
  _activeScreen = screenId;

  document.querySelectorAll('.nav-btn').forEach(btn =>
    btn.classList.toggle('active', btn.dataset.screen === screenId)
  );

  const main = document.getElementById('app-main');
  if (!main) return;
  main.scrollTop = 0;
  main.innerHTML = '';

  const renderFn = SCREENS[screenId];
  if (renderFn) renderFn(main);
}

// ── Header ────────────────────────────────────────────────────────────────────
function initHeader() {
  const hour = new Date().getHours();
  let greeting;
  if (hour < 6)       greeting = 'Good night';
  else if (hour < 12) greeting = 'Good morning';
  else if (hour < 17) greeting = 'Good afternoon';
  else if (hour < 20) greeting = 'Good evening';
  else                greeting = 'Good night';
  setEl('greeting-text', greeting + ', Chef! 👨‍🍳');

  const dateStr = new Date().toLocaleDateString('en-IN', {
    weekday: 'short', day: 'numeric', month: 'short', year: 'numeric'
  });
  setEl('today-date', dateStr);
}

// ── API Status Dot ────────────────────────────────────────────────────────────
async function checkApiStatus() {
  const dot = document.getElementById('api-dot');
  if (!dot) return;
  try {
    const res = await fetch(`${BASE_URL}/health`, { signal: AbortSignal.timeout(3000) });
    if (res.ok) {
      dot.classList.add('online');
      dot.classList.remove('offline');
      dot.title = 'API Online ✓';
    } else throw new Error();
  } catch {
    dot.classList.add('offline');
    dot.classList.remove('online');
    dot.title = 'API Offline — using mock data';
  }
}

// ── Toast ─────────────────────────────────────────────────────────────────────
let _toastTimer = null;
function showToast(message, type = '') {
  const el = document.getElementById('toast');
  if (!el) return;
  el.textContent = message;
  el.className = `toast ${type} show`;
  clearTimeout(_toastTimer);
  _toastTimer = setTimeout(() => { el.className = 'toast'; }, 3200);
}

// ── Utilities ─────────────────────────────────────────────────────────────────
function setEl(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

// ── Splash ────────────────────────────────────────────────────────────────────
function hideSplash() {
  setTimeout(() => {
    const splash = document.getElementById('splash');
    if (splash) splash.classList.add('hidden');
  }, 2000);
}

// ── Chart.js global defaults ───────────────────────────────────────────────────
if (typeof Chart !== 'undefined') {
  Chart.defaults.color = '#8B90B0';
  Chart.defaults.font.family = "'Inter', sans-serif";
  Chart.defaults.borderColor = '#2E3450';
}

// ── Init ──────────────────────────────────────────────────────────────────────
function initApp() {
  initHeader();
  checkApiStatus();
  // Re-check API status every 60s
  setInterval(checkApiStatus, 60000);

  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => navigateTo(btn.dataset.screen));
  });

  navigateTo('dashboard');
  hideSplash();
}

document.addEventListener('DOMContentLoaded', initApp);
