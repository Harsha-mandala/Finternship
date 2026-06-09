# 👤 Person 3 — Frontend Developer + UI/UX + Testing & Demo
## Hotel Aditya Grand · AI Kitchen Order Assistant · POC

---

> **Your Role**: You are the face of the project.
> The merchant only interacts with what you build.
> A brilliant recommendation engine means nothing
> if the app is confusing or ugly on a mobile screen.
> You also own the final demo recording and GitHub submission.

---

## 🎯 What You Own

| Area | Your Responsibility |
|---|---|
| Web App Shell | Project structure, routing, mobile-first layout |
| Design System | Colors, fonts, spacing, component styles |
| Screen 1 — Dashboard | Revenue summary, weather card, top items chart |
| Screen 2 — Recommendations | Tomorrow's order list with reasons + override |
| Screen 3 — Log Sales | Daily sales entry form |
| Screen 4 — Trends | 30-day charts per item, category breakdown |
| API Integration | Connect all screens to Person 1's backend API |
| Testing | Full end-to-end flow testing across screens |
| Demo Prep | Record Loom video, prepare GitHub repo |

---

## 📦 Your Tech Stack

| Tool | Purpose |
|---|---|
| **HTML5** | Structure (semantic, accessible) |
| **Vanilla CSS** | Styling — you will build a full design system |
| **Vanilla JavaScript** | Logic, API calls, interactivity |
| **Chart.js** | Revenue trend + item sales charts |
| **Google Fonts** | Typography (Outfit + Inter) |
| **Fetch API** | Call Person 1's FastAPI backend |
| **LocalStorage** | Cache last-used data for offline-like feel |
| **Vercel** | Deploy your frontend (free, instant) |

---

## 📁 Your Project Folder Structure

```
project/
└── frontend/
    ├── index.html              ← App shell with navigation
    ├── css/
    │   ├── reset.css           ← CSS reset
    │   ├── tokens.css          ← Design tokens (colors, fonts, spacing)
    │   └── components.css      ← All component styles
    ├── js/
    │   ├── api.js              ← All API call functions (central)
    │   ├── dashboard.js        ← Dashboard screen logic
    │   ├── recommendations.js  ← Recommendations screen logic
    │   ├── log-sales.js        ← Log sales screen logic
    │   ├── trends.js           ← Trends screen logic
    │   └── app.js              ← Navigation + app init
    └── assets/
        └── logo.png            ← Hotel Aditya Grand logo (or placeholder)
```

---

## 🎨 Design System (Build This First — Day 1)

### Colour Palette (`tokens.css`)

```css
:root {
  /* Brand */
  --color-primary:       #E8531A;   /* warm saffron-orange */
  --color-primary-dark:  #C4400F;
  --color-primary-light: #FFF0EA;

  /* Backgrounds */
  --color-bg:            #0F1117;   /* near-black */
  --color-surface:       #1A1D27;   /* dark card */
  --color-surface-2:     #22263A;   /* slightly lighter card */
  --color-border:        #2E3450;

  /* Text */
  --color-text:          #F0F2FF;
  --color-text-muted:    #8B90B0;
  --color-text-dim:      #4F5470;

  /* Semantic */
  --color-success:       #22C55E;
  --color-warning:       #F59E0B;
  --color-danger:        #EF4444;
  --color-info:          #3B82F6;

  /* Category colors */
  --color-biryani:       #F97316;
  --color-chicken:       #EF4444;
  --color-beverage:      #06B6D4;
  --color-ice-cream:     #EC4899;
  --color-bread:         #D97706;
  --color-seafood:       #6366F1;

  /* Spacing */
  --space-xs:  4px;
  --space-sm:  8px;
  --space-md:  16px;
  --space-lg:  24px;
  --space-xl:  40px;

  /* Radii */
  --radius-sm:  8px;
  --radius-md:  12px;
  --radius-lg:  20px;
  --radius-pill: 999px;

  /* Shadows */
  --shadow-card: 0 4px 24px rgba(0,0,0,0.4);
  --shadow-glow: 0 0 20px rgba(232,83,26,0.15);
}
```

### Typography

```css
/* In index.html <head> */
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Inter:wght@400;500&display=swap" rel="stylesheet">

/* In tokens.css */
body {
  font-family: 'Inter', sans-serif;
  font-size: 15px;
  background: var(--color-bg);
  color: var(--color-text);
  -webkit-font-smoothing: antialiased;
}

h1, h2, h3, .display {
  font-family: 'Outfit', sans-serif;
  letter-spacing: -0.02em;
}
```

---

## 📐 App Structure (`index.html`)

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
  <meta name="description" content="AI-powered daily order assistant for Hotel Aditya Grand, Kandukur">
  <title>Aditya Grand · Order Assistant</title>
  <link rel="stylesheet" href="css/reset.css">
  <link rel="stylesheet" href="css/tokens.css">
  <link rel="stylesheet" href="css/components.css">
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Inter:wght@400;500&display=swap" rel="stylesheet">
</head>
<body>

  <!-- Top Header -->
  <header class="app-header" id="app-header">
    <div class="header-left">
      <div class="hotel-logo">🏨</div>
      <div>
        <div class="hotel-name">Aditya Grand</div>
        <div class="hotel-sub" id="greeting-text">Good morning</div>
      </div>
    </div>
    <div class="header-right">
      <div class="date-badge" id="today-date"></div>
    </div>
  </header>

  <!-- Main Content Area -->
  <main class="app-main" id="app-main">
    <!-- Screens are injected here by JS -->
  </main>

  <!-- Bottom Navigation -->
  <nav class="bottom-nav" id="bottom-nav">
    <button class="nav-btn active" data-screen="dashboard" id="nav-dashboard">
      <span class="nav-icon">📊</span>
      <span class="nav-label">Dashboard</span>
    </button>
    <button class="nav-btn" data-screen="recommendations" id="nav-recommendations">
      <span class="nav-icon">🧠</span>
      <span class="nav-label">Orders</span>
    </button>
    <button class="nav-btn" data-screen="log-sales" id="nav-log-sales">
      <span class="nav-icon">✏️</span>
      <span class="nav-label">Log Sales</span>
    </button>
    <button class="nav-btn" data-screen="trends" id="nav-trends">
      <span class="nav-icon">📈</span>
      <span class="nav-label">Trends</span>
    </button>
  </nav>

  <script src="js/api.js"></script>
  <script src="js/dashboard.js"></script>
  <script src="js/recommendations.js"></script>
  <script src="js/log-sales.js"></script>
  <script src="js/trends.js"></script>
  <script src="js/app.js"></script>
</body>
</html>
```

---

## 📅 Week-by-Week Task Breakdown

---

### ✅ WEEK 1 — Foundations & Static UI

#### Day 1: CSS Reset + Design Tokens

Build `reset.css`, `tokens.css`, and skeleton `components.css`. Include:
- Card component (`.card`, `.card-dark`)
- Badge (`.badge`, `.badge-success`, `.badge-warning`)
- Button (`.btn`, `.btn-primary`, `.btn-ghost`)
- Input (`.input-field`, `.qty-stepper`)
- Bottom navigation (`.bottom-nav`, `.nav-btn`)
- Header (`.app-header`)

#### Day 2: Central API Module (`api.js`)

This is the **most important JS file**. All API calls go here.

```javascript
// api.js

// Change this to Person 1's live Render URL once deployed
// During development, use: http://localhost:8000
const BASE_URL = window.location.hostname === 'localhost'
  ? 'http://localhost:8000'
  : 'https://hotel-aditya-api.onrender.com';  // UPDATE when deployed

async function apiFetch(path, options = {}) {
  try {
    const res = await fetch(`${BASE_URL}${path}`, {
      headers: { 'Content-Type': 'application/json' },
      ...options
    });
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error('API call failed:', path, err);
    return null;
  }
}

// Dashboard
const API = {
  getDashboardSummary: () => apiFetch('/dashboard/summary'),
  getRevenueTrend: (days = 30) => apiFetch(`/dashboard/revenue-trend?days=${days}`),

  // Items
  getAllItems: () => apiFetch('/items/'),

  // Sales
  getSalesByDate: (date) => apiFetch(`/sales/?date=${date}`),
  logSales: (entries) => apiFetch('/sales/log', {
    method: 'POST',
    body: JSON.stringify(entries)
  }),
  getItemTrend: (item, days = 30) => apiFetch(`/sales/trends?item=${encodeURIComponent(item)}&days=${days}`),

  // Recommendations
  getRecommendations: (date) => apiFetch(`/recommendations/?date=${date}`),
  overrideRecommendation: (item_name, date, qty) => apiFetch('/recommendations/override', {
    method: 'PUT',
    body: JSON.stringify({ item_name, date, merchant_qty: qty })
  }),
};
```

#### Day 3–5: Build Static Screens

Build all 4 screens with **hardcoded mock data first** (before the API is ready).

**Mock data to hardcode while waiting for API**:
```javascript
// In each screen JS file, use this until API is ready:
const MOCK_DASHBOARD = {
  today_revenue: 52340,
  top_items: [
    { item_name: "Chicken Dum Biryani", qty: 18 },
    { item_name: "Cool Drink 250ml", qty: 31 },
    { item_name: "Butter Naan", qty: 24 },
    { item_name: "Chilli Chicken BL", qty: 11 },
    { item_name: "Curd Rice", qty: 8 }
  ],
  weather: { condition: "Clear", max_temp: 38, rainfall_mm: 0 },
  upcoming_festival: null
};
```

---

### ✅ WEEK 2 — Build Each Screen Fully

#### Screen 1: Dashboard (`dashboard.js`)

**What to show**:
- Greeting: "Good morning, Chef! 🌅" (changes by time of day)
- Today's date
- Weather card: condition icon + temp + rain alert if applicable
- Upcoming festival banner (if within 3 days)
- Revenue card: "Today's Gross: ₹52,340"
- Top 5 items chart (horizontal bar chart with Chart.js)

```javascript
// dashboard.js

function renderDashboard(container) {
  container.innerHTML = `
    <div class="screen-dashboard">
      <div class="weather-card" id="weather-card">
        <div class="weather-icon" id="weather-icon">☀️</div>
        <div class="weather-info">
          <div class="weather-temp" id="weather-temp">--°C</div>
          <div class="weather-desc" id="weather-desc">Loading weather...</div>
        </div>
        <div class="weather-tag" id="weather-tag"></div>
      </div>

      <div class="festival-banner" id="festival-banner" style="display:none">
        🎉 <span id="festival-name"></span> tomorrow — orders will be higher!
      </div>

      <div class="stat-row">
        <div class="card stat-card">
          <div class="stat-label">Today's Revenue</div>
          <div class="stat-value" id="today-revenue">₹ --</div>
        </div>
        <div class="card stat-card">
          <div class="stat-label">Items Sold</div>
          <div class="stat-value" id="items-sold">--</div>
        </div>
      </div>

      <div class="card chart-card">
        <div class="card-title">🔥 Top Items Today</div>
        <canvas id="top-items-chart" height="220"></canvas>
      </div>
    </div>
  `;

  loadDashboardData();
}

async function loadDashboardData() {
  const data = await API.getDashboardSummary();
  if (!data) return;

  // Weather
  const weatherIcons = { Clear:'☀️', Rain:'🌧️', Clouds:'⛅', Thunderstorm:'⛈️' };
  document.getElementById('weather-icon').textContent = weatherIcons[data.weather?.condition] || '🌡️';
  document.getElementById('weather-temp').textContent = `${data.weather?.max_temp}°C`;
  document.getElementById('weather-desc').textContent = data.weather?.condition || '--';
  if (data.weather?.rainfall_mm > 2) {
    document.getElementById('weather-tag').textContent = '🌧️ Rain Alert';
    document.getElementById('weather-tag').classList.add('tag-warning');
  }

  // Festival
  if (data.upcoming_festival) {
    document.getElementById('festival-banner').style.display = 'flex';
    document.getElementById('festival-name').textContent = data.upcoming_festival;
  }

  // Stats
  document.getElementById('today-revenue').textContent = `₹${data.today_revenue?.toLocaleString('en-IN') || 0}`;
  document.getElementById('items-sold').textContent = data.total_qty_sold || '--';

  // Chart
  renderTopItemsChart(data.top_items || []);
}

function renderTopItemsChart(items) {
  const ctx = document.getElementById('top-items-chart').getContext('2d');
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: items.map(i => i.item_name.length > 20 ? i.item_name.slice(0,18)+'…' : i.item_name),
      datasets: [{
        data: items.map(i => i.qty),
        backgroundColor: ['#E8531A','#F97316','#FBBF24','#34D399','#60A5FA'],
        borderRadius: 8,
      }]
    },
    options: {
      indexAxis: 'y',
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { color: '#2E3450' }, ticks: { color: '#8B90B0' } },
        y: { grid: { display: false }, ticks: { color: '#F0F2FF' } }
      }
    }
  });
}
```

---

#### Screen 2: Recommendations (`recommendations.js`)

This is the **most important screen**. Make it clear, fast, and action-oriented.

**What to show**:
- Date selector (default: tomorrow)
- Context card: "📅 [Date] · ☀️ 38°C · No festivals"
- Recommendation list grouped by category (Biryani, Chicken, Beverages, etc.)
- Each item card: Item name | Recommended qty | Reason pill | Edit button
- "Confirm All Orders" button at bottom
- Loading skeleton while fetching

```javascript
// recommendations.js

function renderRecommendations(container) {
  container.innerHTML = `
    <div class="screen-recs">
      <div class="date-selector-row">
        <label class="label-sm">Ordering for</label>
        <input type="date" id="rec-date" class="input-field date-input">
      </div>

      <div class="context-card card" id="rec-context">
        <div class="context-loading">Loading context...</div>
      </div>

      <div id="rec-list" class="rec-list">
        <div class="skeleton-list">
          ${Array(8).fill('<div class="skeleton-item"></div>').join('')}
        </div>
      </div>

      <div class="sticky-footer">
        <button class="btn btn-primary btn-full" id="confirm-orders-btn" onclick="confirmOrders()">
          ✅ Confirm All Orders
        </button>
      </div>
    </div>
  `;

  // Set default date to tomorrow
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  document.getElementById('rec-date').value = tomorrow.toISOString().split('T')[0];

  document.getElementById('rec-date').addEventListener('change', (e) => {
    loadRecommendations(e.target.value);
  });

  loadRecommendations(document.getElementById('rec-date').value);
}

async function loadRecommendations(date) {
  document.getElementById('rec-list').innerHTML = '<div class="loading-spinner"></div>';
  const data = await API.getRecommendations(date);
  if (!data) {
    document.getElementById('rec-list').innerHTML = '<div class="empty-state">Could not load recommendations. Is the server running?</div>';
    return;
  }

  // Group by category
  const grouped = {};
  data.recommendations.forEach(rec => {
    const cat = rec.category || 'other';
    if (!grouped[cat]) grouped[cat] = [];
    grouped[cat].push(rec);
  });

  const CATEGORY_LABELS = {
    biryani: '🍛 Biryanis', chicken: '🍗 Chicken', beverage: '🥤 Beverages',
    ice_cream: '🍦 Ice Creams', bread: '🫓 Breads', rice: '🍚 Rice',
    starter: '🍟 Starters', seafood: '🦐 Seafood', egg: '🥚 Eggs',
    family_pack: '📦 Family Packs', other: '🍽️ Others'
  };

  let html = '';
  for (const [cat, items] of Object.entries(grouped)) {
    html += `
      <div class="cat-section">
        <div class="cat-header">${CATEGORY_LABELS[cat] || cat}</div>
        ${items.map(rec => `
          <div class="rec-card card" id="rec-card-${rec.item_name.replace(/\s/g,'_')}">
            <div class="rec-left">
              <div class="rec-item-name">${rec.item_name}</div>
              <div class="rec-reason">${rec.reason}</div>
            </div>
            <div class="rec-right">
              <div class="qty-stepper">
                <button class="stepper-btn" onclick="changeQty('${rec.item_name}', -1, '${date}')">−</button>
                <span class="qty-value" id="qty-${rec.item_name.replace(/\s/g,'_')}">${rec.recommended_qty}</span>
                <button class="stepper-btn" onclick="changeQty('${rec.item_name}', 1, '${date}')">+</button>
              </div>
            </div>
          </div>
        `).join('')}
      </div>`;
  }
  document.getElementById('rec-list').innerHTML = html;
}

function changeQty(itemName, delta, date) {
  const key = itemName.replace(/\s/g, '_');
  const el = document.getElementById(`qty-${key}`);
  const current = parseInt(el.textContent);
  const newQty = Math.max(0, current + delta);
  el.textContent = newQty;
  API.overrideRecommendation(itemName, date, newQty);
}

function confirmOrders() {
  const btn = document.getElementById('confirm-orders-btn');
  btn.textContent = '✅ Orders Confirmed!';
  btn.style.background = 'var(--color-success)';
  setTimeout(() => {
    btn.textContent = '✅ Confirm All Orders';
    btn.style.background = '';
  }, 2000);
}
```

---

#### Screen 3: Log Sales (`log-sales.js`)

```javascript
// log-sales.js

function renderLogSales(container) {
  container.innerHTML = `
    <div class="screen-log">
      <div class="log-header">
        <h2 class="screen-title">Log Today's Sales</h2>
        <input type="date" id="log-date" class="input-field">
      </div>

      <div class="search-row">
        <input type="text" id="item-search" class="input-field" placeholder="Search items...">
      </div>

      <div id="sales-form" class="sales-form">
        <div class="loading-spinner"></div>
      </div>

      <div class="sticky-footer">
        <button class="btn btn-primary btn-full" id="save-sales-btn" onclick="saveSales()">
          💾 Save Sales Data
        </button>
      </div>
    </div>
  `;

  // Set today's date
  document.getElementById('log-date').value = new Date().toISOString().split('T')[0];

  // Search filter
  document.getElementById('item-search').addEventListener('input', (e) => {
    const q = e.target.value.toLowerCase();
    document.querySelectorAll('.sales-item-row').forEach(row => {
      row.style.display = row.dataset.item.toLowerCase().includes(q) ? 'flex' : 'none';
    });
  });

  loadSalesForm();
}

async function loadSalesForm() {
  const items = await API.getAllItems();
  const today = document.getElementById('log-date').value;
  const todaySales = await API.getSalesByDate(today);
  const todayMap = {};
  (todaySales || []).forEach(s => todayMap[s.item_name] = s.qty_sold);

  // Sort by popularity (high-volume items first)
  const sortedItems = (items || []).sort((a, b) => b.avg_qty - a.avg_qty);

  const html = sortedItems.map(item => `
    <div class="sales-item-row" data-item="${item.item_name}">
      <div class="sales-item-name">${item.item_name}</div>
      <div class="qty-stepper compact">
        <button class="stepper-btn sm" onclick="this.nextElementSibling.value=Math.max(0,+this.nextElementSibling.value-1)">−</button>
        <input type="number" class="qty-input" data-item="${item.item_name}"
               value="${todayMap[item.item_name] || 0}" min="0" step="1">
        <button class="stepper-btn sm" onclick="this.previousElementSibling.value=+this.previousElementSibling.value+1">+</button>
      </div>
    </div>
  `).join('');

  document.getElementById('sales-form').innerHTML = html || '<p class="empty-state">No items found</p>';
}

async function saveSales() {
  const date = document.getElementById('log-date').value;
  const entries = [];
  document.querySelectorAll('.qty-input').forEach(input => {
    const qty = parseInt(input.value);
    if (qty > 0) {
      entries.push({ date, item_name: input.dataset.item, qty_sold: qty });
    }
  });

  if (entries.length === 0) {
    alert('Please enter at least one item quantity.');
    return;
  }

  const result = await API.logSales(entries);
  if (result) {
    const btn = document.getElementById('save-sales-btn');
    btn.textContent = `✅ Saved ${result.logged} items!`;
    setTimeout(() => btn.textContent = '💾 Save Sales Data', 2500);
  }
}
```

---

#### Screen 4: Trends (`trends.js`)

```javascript
// trends.js

function renderTrends(container) {
  container.innerHTML = `
    <div class="screen-trends">
      <div class="card">
        <div class="card-title">📈 30-Day Revenue Trend</div>
        <canvas id="revenue-chart" height="180"></canvas>
      </div>

      <div class="card" style="margin-top: var(--space-md)">
        <div class="card-title">🔍 Item Deep-Dive</div>
        <select id="item-selector" class="input-field">
          <option>Loading items...</option>
        </select>
        <canvas id="item-chart" height="160" style="margin-top: var(--space-md)"></canvas>
      </div>

      <div class="card" style="margin-top: var(--space-md)">
        <div class="card-title">📊 Sales by Category</div>
        <canvas id="category-chart" height="200"></canvas>
      </div>
    </div>
  `;

  loadTrendsData();
}

async function loadTrendsData() {
  // Revenue trend chart
  const trendData = await API.getRevenueTrend(30);
  if (trendData) {
    const ctx = document.getElementById('revenue-chart').getContext('2d');
    new Chart(ctx, {
      type: 'line',
      data: {
        labels: trendData.map(d => d.date.slice(5)),  // MM-DD
        datasets: [{
          label: 'Revenue (₹)',
          data: trendData.map(d => d.revenue),
          borderColor: '#E8531A',
          backgroundColor: 'rgba(232,83,26,0.1)',
          fill: true,
          tension: 0.4,
          pointRadius: 3,
        }]
      },
      options: {
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: '#2E3450' }, ticks: { color: '#8B90B0', maxRotation: 45 } },
          y: { grid: { color: '#2E3450' }, ticks: { color: '#8B90B0',
               callback: v => '₹'+v.toLocaleString('en-IN') } }
        }
      }
    });
  }

  // Populate item selector
  const items = await API.getAllItems();
  const selector = document.getElementById('item-selector');
  if (items) {
    selector.innerHTML = items.map(i => `<option value="${i.item_name}">${i.item_name}</option>`).join('');
    selector.addEventListener('change', () => loadItemChart(selector.value));
    loadItemChart(items[0]?.item_name);
  }
}

let itemChart = null;
async function loadItemChart(itemName) {
  const data = await API.getItemTrend(itemName, 30);
  if (!data) return;
  if (itemChart) itemChart.destroy();

  const ctx = document.getElementById('item-chart').getContext('2d');
  itemChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: data.map(d => d.date.slice(5)),
      datasets: [{
        label: 'Qty Sold',
        data: data.map(d => d.qty),
        backgroundColor: '#E8531A88',
        borderColor: '#E8531A',
        borderWidth: 1,
        borderRadius: 4,
      }]
    },
    options: {
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { color: '#2E3450' }, ticks: { color: '#8B90B0' } },
        y: { grid: { color: '#2E3450' }, ticks: { color: '#8B90B0' } }
      }
    }
  });
}
```

---

#### App Navigation (`app.js`)

```javascript
// app.js

const SCREENS = {
  dashboard:       renderDashboard,
  recommendations: renderRecommendations,
  'log-sales':     renderLogSales,
  trends:          renderTrends,
};

function navigateTo(screen) {
  const main = document.getElementById('app-main');
  SCREENS[screen](main);

  // Update nav active state
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.screen === screen);
  });
}

// Init
document.addEventListener('DOMContentLoaded', () => {
  // Set greeting
  const hour = new Date().getHours();
  document.getElementById('greeting-text').textContent =
    hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening';

  // Set today date
  document.getElementById('today-date').textContent =
    new Date().toLocaleDateString('en-IN', { day:'numeric', month:'short', weekday:'short' });

  // Nav click handlers
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => navigateTo(btn.dataset.screen));
  });

  // Import Chart.js dynamically
  const script = document.createElement('script');
  script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
  script.onload = () => navigateTo('dashboard');
  document.head.appendChild(script);
});
```

---

### ✅ WEEK 3 — Polish, Testing & Demo

#### Testing Checklist (You Own This):
- [ ] All 4 screens load without JS errors
- [ ] Dashboard shows real weather and revenue data
- [ ] Recommendations screen shows grouped items with reasons
- [ ] Override qty updates via API (check network tab)
- [ ] Log sales saves data correctly (check `/sales/?date=today`)
- [ ] Trends charts render properly
- [ ] App works on mobile screen (375px width) — test in Chrome DevTools
- [ ] App works on Safari iOS (if possible)
- [ ] API error states handled gracefully (no blank screens)
- [ ] Fonts load from Google Fonts
- [ ] Charts are readable with dark background

#### Deploy to Vercel:
1. Push `frontend/` to GitHub
2. Go to [vercel.com](https://vercel.com) → New Project → import your repo
3. Set root directory to `frontend/`
4. Deploy — you get a live URL instantly
5. Share URL with team and with Marripudi Akhil

#### Record the Demo (Loom):
**Script for the 5-minute demo video**:

1. **(0:00)** Open app on mobile (screen mirror or phone) — show Dashboard
2. **(1:00)** "Tomorrow it's going to rain — let's see how the system adjusts orders"
3. **(1:30)** Tap Recommendations tab → show Chicken Dum Biryani is UP, Cool Drinks are DOWN
4. **(2:30)** Show override feature — change one qty by +3
5. **(3:00)** Go to Log Sales — enter today's quantities
6. **(4:00)** Go to Trends — show the 30-day revenue chart
7. **(4:30)** Summarize: "This replaces guesswork with data — saving ₹4,000+ weekly"

#### GitHub Repo Structure:
```
hotel-aditya-order-ai/
├── README.md            ← Project description + live links
├── frontend/            ← Your code
├── backend/             ← Person 1's code
├── data_pipeline/       ← Person 1's PDF parser
├── analysis/            ← Person 2's notebooks
└── data/
    └── festivals_2026.json
```

Send GitHub repo link + Loom recording to: **finternship@okcredit.in**

---

## 📤 What You Hand Off / Deliver

| Deliverable | For | Deadline |
|---|---|---|
| Live frontend URL (Vercel) | Akhil demo | End of Week 3 |
| GitHub repo (frontend code) | OKCredit submission | End of Week 3 |
| Loom demo recording | OKCredit submission | End of Week 3 |
| Test report (bugs found) | Team quality check | End of Week 3 |

---

## ✅ Final Deliverables Checklist

- [ ] All 4 screens built and connected to live API
- [ ] Design system implemented (dark theme, Outfit font, orange brand)
- [ ] Charts working (revenue trend, top items, item deep-dive)
- [ ] Mobile responsive (works on 375px+)
- [ ] Deployed to Vercel with live URL
- [ ] API error states handled gracefully
- [ ] Demo video recorded (Loom, 4-6 minutes)
- [ ] GitHub repo organized with README
- [ ] Submitted to finternship@okcredit.in
