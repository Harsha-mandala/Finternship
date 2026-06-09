/* ═══════════════════════════════════════════════════════════
   dashboard.js — Screen 1
   ═══════════════════════════════════════════════════════════ */

let _dashChart = null;

function renderDashboard(container) {
  container.innerHTML = `
    <div class="screen">
      <!-- Weather -->
      <div class="weather-card" id="weather-card">
        <div class="weather-left">
          <div class="weather-icon" id="weather-icon">🌡️</div>
          <div>
            <div class="weather-temp" id="weather-temp">--°C</div>
            <div class="weather-desc" id="weather-desc">Loading...</div>
          </div>
        </div>
        <div class="weather-tags" id="weather-tags"></div>
      </div>

      <!-- Festival Banner -->
      <div class="festival-banner hidden" id="festival-banner">
        🎉 <span id="festival-name"></span>
      </div>

      <!-- Revenue Highlight -->
      <div class="revenue-highlight">
        <div class="rev-label">Today's Gross Revenue</div>
        <div class="rev-amount" id="today-revenue">₹ —</div>
        <div class="rev-sub" id="revenue-sub">Loading...</div>
      </div>

      <!-- Mini Stats -->
      <div class="mini-bar">
        <div class="mini-stat">
          <div class="mini-stat-val" id="items-sold">—</div>
          <div class="mini-stat-lbl">Units Sold</div>
        </div>
        <div class="mini-stat">
          <div class="mini-stat-val" id="avg-order">—</div>
          <div class="mini-stat-lbl">Avg / Item</div>
        </div>
        <div class="mini-stat">
          <div class="mini-stat-val" id="top-cat">—</div>
          <div class="mini-stat-lbl">Top Category</div>
        </div>
      </div>

      <!-- Top Items Chart -->
      <div class="card chart-card">
        <div class="card-title">🔥 Top Items Today</div>
        <canvas id="top-items-chart" height="240"></canvas>
      </div>

      <!-- Revenue Trend -->
      <div class="card chart-card">
        <div class="card-title">📈 14-Day Revenue Trend</div>
        <canvas id="revenue-trend-chart" height="180"></canvas>
      </div>
    </div>
  `;

  loadDashboardData();
}

async function loadDashboardData() {
  const data = await API.getDashboardSummary();
  if (!data) return;

  // ── Weather ──────────────────────────────────────────────────────────────────
  const WEATHER_ICONS = {
    Clear: '☀️', Rain: '🌧️', Clouds: '⛅',
    Thunderstorm: '⛈️', Drizzle: '🌦️', Mist: '🌫️'
  };
  const w = data.weather || {};
  const icon = WEATHER_ICONS[w.condition] || '🌡️';
  document.getElementById('weather-icon').textContent = icon;
  document.getElementById('weather-temp').textContent = w.max_temp ? `${Math.round(w.max_temp)}°C` : '--°C';
  document.getElementById('weather-desc').textContent = w.condition || '--';

  const tagsEl = document.getElementById('weather-tags');
  let tagHtml = '';
  if (w.rainfall_mm > 2) tagHtml += `<div class="weather-tag tag-rain">🌧️ Rain</div>`;
  if (w.max_temp >= 39) tagHtml += `<div class="weather-tag tag-hot">🔥 Hot</div>`;
  if (w.condition === 'Clear' && w.max_temp < 38) tagHtml += `<div class="weather-tag tag-clear">✓ Clear</div>`;
  tagsEl.innerHTML = tagHtml;

  // ── Festival ──────────────────────────────────────────────────────────────────
  const fest = data.upcoming_festival || data.festival_today;
  if (fest) {
    document.getElementById('festival-banner').classList.remove('hidden');
    document.getElementById('festival-name').textContent = `${fest} — expect higher demand!`;
  }

  // ── Revenue ───────────────────────────────────────────────────────────────────
  const rev = data.today_revenue || 0;
  document.getElementById('today-revenue').textContent = `₹${rev.toLocaleString('en-IN')}`;
  const qty = data.total_qty_sold || 0;
  document.getElementById('revenue-sub').textContent = `${qty} units sold today`;

  // ── Mini stats ────────────────────────────────────────────────────────────────
  document.getElementById('items-sold').textContent = qty.toLocaleString('en-IN');
  const avgPerItem = qty > 0 ? Math.round(rev / qty) : 0;
  document.getElementById('avg-order').textContent = `₹${avgPerItem}`;

  const topItems = data.top_items || [];
  if (topItems.length > 0) {
    const topCatName = topItems[0].item_name || '';
    document.getElementById('top-cat').textContent = topCatName.split(' ').slice(0, 2).join(' ');
  }

  // ── Charts ────────────────────────────────────────────────────────────────────
  if (topItems.length) renderTopItemsChart(topItems);

  // Revenue trend
  const trendData = await API.getRevenueTrend(14);
  if (trendData && trendData.length) renderRevenueTrend(trendData);
}

function renderTopItemsChart(items) {
  const el = document.getElementById('top-items-chart');
  if (!el) return;

  if (_dashChart) { _dashChart.destroy(); _dashChart = null; }

  const PALETTE = ['#E8531A','#F97316','#FBBF24','#34D399','#60A5FA'];
  const ctx = el.getContext('2d');
  _dashChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: items.map(i => i.item_name.length > 22 ? i.item_name.slice(0, 20) + '…' : i.item_name),
      datasets: [{
        data: items.map(i => i.qty || i.qty_sold || 0),
        backgroundColor: items.map((_, idx) => PALETTE[idx % PALETTE.length]),
        borderRadius: 8,
        borderSkipped: false,
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#1A1D27',
          borderColor: '#2E3450',
          borderWidth: 1,
          titleColor: '#F0F2FF',
          bodyColor: '#8B90B0',
          callbacks: { label: (ctx) => ` ${ctx.parsed.x} units` }
        }
      },
      scales: {
        x: {
          grid: { color: '#2E3450' },
          ticks: { color: '#8B90B0', font: { size: 11 } }
        },
        y: {
          grid: { display: false },
          ticks: { color: '#F0F2FF', font: { size: 12, weight: '500' } }
        }
      },
      animation: { duration: 600, easing: 'easeOutQuart' }
    }
  });
}

function renderRevenueTrend(trendData) {
  const el = document.getElementById('revenue-trend-chart');
  if (!el) return;

  const labels = trendData.map(d => {
    const dt = new Date(d.date);
    return dt.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
  });
  const values = trendData.map(d => d.revenue || d.total_revenue || 0);

  const ctx = el.getContext('2d');
  new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        data: values,
        borderColor: '#E8531A',
        backgroundColor: (context) => {
          const chart = context.chart;
          const { ctx: c, chartArea } = chart;
          if (!chartArea) return 'transparent';
          const gradient = c.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
          gradient.addColorStop(0, 'rgba(232,83,26,0.25)');
          gradient.addColorStop(1, 'rgba(232,83,26,0)');
          return gradient;
        },
        borderWidth: 2.5,
        fill: true,
        tension: 0.4,
        pointRadius: 3,
        pointBackgroundColor: '#E8531A',
        pointBorderColor: '#0F1117',
        pointBorderWidth: 2,
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#1A1D27',
          borderColor: '#2E3450', borderWidth: 1,
          titleColor: '#F0F2FF', bodyColor: '#8B90B0',
          callbacks: {
            label: (ctx) => ` ₹${Math.round(ctx.parsed.y).toLocaleString('en-IN')}`
          }
        }
      },
      scales: {
        x: { grid: { display: false }, ticks: { color: '#8B90B0', font: { size: 10 }, maxTicksLimit: 7 } },
        y: {
          grid: { color: '#2E3450' },
          ticks: {
            color: '#8B90B0', font: { size: 10 },
            callback: v => `₹${(v / 1000).toFixed(0)}k`
          }
        }
      },
      animation: { duration: 800, easing: 'easeOutQuart' }
    }
  });
}
