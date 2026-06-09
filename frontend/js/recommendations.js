/* ═══════════════════════════════════════════════════════════
   recommendations.js — Screen 2 (Most Important Screen)
   ═══════════════════════════════════════════════════════════ */

const CATEGORY_META = {
  biryani:     { label: '🍛 Biryanis',       color: '#F97316' },
  chicken:     { label: '🍗 Chicken',         color: '#EF4444' },
  beverage:    { label: '🥤 Beverages',       color: '#06B6D4' },
  ice_cream:   { label: '🍦 Ice Creams',      color: '#EC4899' },
  bread:       { label: '🫓 Breads & Rotis',  color: '#D97706' },
  rice:        { label: '🍚 Rice Items',      color: '#F59E0B' },
  starter:     { label: '🍟 Starters',        color: '#84CC16' },
  seafood:     { label: '🦐 Seafood',         color: '#6366F1' },
  egg:         { label: '🥚 Eggs',            color: '#FBBF24' },
  dairy:       { label: '🧀 Dairy & Paneer',  color: '#A78BFA' },
  family_pack: { label: '📦 Family Packs',    color: '#E8531A' },
  soup:        { label: '🍲 Soups',           color: '#14B8A6' },
  other:       { label: '🍽️ Others',          color: '#8B90B0' },
};

// Track modified quantities
let _modifiedQtys = {};
let _currentRecDate = null;

function renderRecommendations(container) {
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  const tomorrowStr = tomorrow.toISOString().split('T')[0];

  container.innerHTML = `
    <div class="screen">
      <!-- Date Selector -->
      <div class="date-selector-row">
        <span class="label-sm">Ordering for</span>
        <input type="date" id="rec-date" class="input-field" value="${tomorrowStr}"
               style="max-width:160px">
      </div>

      <!-- Context Card -->
      <div class="card context-card" id="rec-context">
        <div class="context-pill">⏳ <span>Loading context...</span></div>
      </div>

      <!-- Recommendation List -->
      <div id="rec-list" class="rec-list">
        ${skeletonList(8)}
      </div>

      <!-- Confirm Button -->
      <div class="sticky-footer">
        <button class="btn btn-primary btn-full" id="confirm-orders-btn" onclick="confirmOrders()">
          ✅ Confirm All Orders
        </button>
      </div>
    </div>
  `;

  document.getElementById('rec-date').addEventListener('change', (e) => {
    _modifiedQtys = {};
    loadRecommendations(e.target.value);
  });

  loadRecommendations(tomorrowStr);
}

async function loadRecommendations(date) {
  _currentRecDate = date;
  const listEl = document.getElementById('rec-list');
  if (!listEl) return;
  listEl.innerHTML = skeletonList(10);

  // Load context
  loadRecContext(date);

  // Load recommendations
  const data = await API.getRecommendations(date);
  if (!listEl) return;

  if (!data || !data.recommendations || data.recommendations.length === 0) {
    listEl.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">🤖</div>
        <div>No recommendations available.<br>Make sure the backend is running.</div>
      </div>`;
    return;
  }

  const recs = data.recommendations;

  // Group by category in preferred order
  const CAT_ORDER = ['biryani','chicken','bread','dairy','rice','beverage','starter','seafood','ice_cream','family_pack','egg','soup','other'];
  const grouped = {};
  recs.forEach(rec => {
    const cat = rec.category || 'other';
    if (!grouped[cat]) grouped[cat] = [];
    grouped[cat].push(rec);
  });

  let html = '';
  for (const cat of CAT_ORDER) {
    if (!grouped[cat]) continue;
    const meta = CATEGORY_META[cat] || { label: cat, color: '#8B90B0' };
    const items = grouped[cat].sort((a, b) => b.recommended_qty - a.recommended_qty);

    html += `
      <div class="cat-section">
        <div class="cat-header" style="color:${meta.color}">
          <span class="cat-badge" style="background:${meta.color}"></span>${meta.label}
        </div>
        ${items.map(rec => recCard(rec, date)).join('')}
      </div>`;
  }

  // Any remaining categories
  for (const cat of Object.keys(grouped)) {
    if (CAT_ORDER.includes(cat)) continue;
    const meta = CATEGORY_META[cat] || { label: cat, color: '#8B90B0' };
    html += `
      <div class="cat-section">
        <div class="cat-header">${meta.label}</div>
        ${grouped[cat].map(rec => recCard(rec, date)).join('')}
      </div>`;
  }

  listEl.innerHTML = html;
}

function recCard(rec, date) {
  const safeKey = safeId(rec.item_name);
  const qty = _modifiedQtys[rec.item_name] ?? rec.recommended_qty;
  const isModified = _modifiedQtys[rec.item_name] !== undefined;

  const reasonHtml = rec.reason
    ? `<div class="rec-reason" title="${rec.reason}">${rec.reason}</div>`
    : '';

  return `
    <div class="rec-card card ${isModified ? 'modified-card' : ''}" id="rec-card-${safeKey}">
      <div class="rec-left">
        <div class="rec-item-name">${rec.item_name}</div>
        ${reasonHtml}
      </div>
      <div class="rec-right">
        <div class="qty-stepper ${isModified ? 'modified' : ''}" id="stepper-${safeKey}">
          <button class="stepper-btn" onclick="changeQty('${escJs(rec.item_name)}', -1, '${date}')">−</button>
          <span class="qty-value" id="qty-${safeKey}">${qty}</span>
          <button class="stepper-btn" onclick="changeQty('${escJs(rec.item_name)}', 1, '${date}')">+</button>
        </div>
      </div>
    </div>`;
}

async function loadRecContext(date) {
  const ctxEl = document.getElementById('rec-context');
  if (!ctxEl) return;

  const ctx = await API.getRecommendationContext(date);
  if (!ctx) {
    ctxEl.innerHTML = `<div class="context-pill">📅 <span>${fmtDate(date)}</span></div>`;
    return;
  }

  const ICONS = { Clear: '☀️', Rain: '🌧️', Clouds: '⛅', Thunderstorm: '⛈️' };
  const w = ctx.weather || {};
  const weatherStr = w.condition
    ? `${ICONS[w.condition] || '🌡️'} ${Math.round(w.max_temp || 0)}°C ${w.condition}`
    : '—';

  let festStr = ctx.festival_today
    ? `🎉 ${ctx.festival_today}`
    : ctx.upcoming_festivals && ctx.upcoming_festivals.length
    ? `📅 ${ctx.upcoming_festivals[0].name} in ${ctx.upcoming_festivals[0].days_away}d`
    : '✓ No festivals';

  const mult = ctx.festival_mult > 1
    ? `<span class="acc-badge acc-good">+${Math.round((ctx.festival_mult - 1) * 100)}% demand</span>`
    : '';

  ctxEl.innerHTML = `
    <div class="context-pill">📅 <span>${fmtDate(date)}</span></div>
    <div class="context-pill">${weatherStr}</div>
    <div class="context-pill">${festStr} ${mult}</div>
  `;
}

function changeQty(itemName, delta, date) {
  const key = safeId(itemName);
  const el = document.getElementById(`qty-${key}`);
  const stepperEl = document.getElementById(`stepper-${key}`);
  if (!el) return;

  const current = parseInt(el.textContent) || 0;
  const newQty = Math.max(0, current + delta);
  el.textContent = newQty;
  _modifiedQtys[itemName] = newQty;

  // Visual feedback
  if (stepperEl) stepperEl.classList.add('modified');
  el.style.color = 'var(--color-primary)';

  // Debounced API save
  clearTimeout(el._saveTimer);
  el._saveTimer = setTimeout(() => {
    API.overrideRecommendation(itemName, date, newQty);
  }, 800);
}

function confirmOrders() {
  const btn = document.getElementById('confirm-orders-btn');
  if (!btn) return;

  btn.disabled = true;
  btn.textContent = '✅ Orders Confirmed!';
  btn.classList.remove('btn-primary');
  btn.classList.add('btn-success');

  // Save all overrides
  Object.entries(_modifiedQtys).forEach(([item, qty]) => {
    if (_currentRecDate) API.overrideRecommendation(item, _currentRecDate, qty);
  });

  showToast('Orders confirmed and saved!', 'success');

  setTimeout(() => {
    btn.disabled = false;
    btn.textContent = '✅ Confirm All Orders';
    btn.classList.remove('btn-success');
    btn.classList.add('btn-primary');
  }, 3000);
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function safeId(str) { return str.replace(/[^a-zA-Z0-9]/g, '_'); }
function escJs(str) { return str.replace(/'/g, "\\'").replace(/"/g, '\\"'); }
function fmtDate(dateStr) {
  const d = new Date(dateStr + 'T00:00:00');
  return d.toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short' });
}
function skeletonList(n) {
  return `<div class="skeleton-list">${Array(n).fill('<div class="skeleton skeleton-item"></div>').join('')}</div>`;
}
