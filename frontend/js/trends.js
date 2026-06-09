/* ═══════════════════════════════════════════════════════════
   trends.js — Screen 4
   ═══════════════════════════════════════════════════════════ */

let _trendsCharts = {};
let _activeTab = 'revenue';

function renderTrends(container) {
  container.innerHTML = `
    <div class="screen">
      <div class="screen-title" style="margin-bottom:12px;">Analytics</div>

      <!-- Tab Row -->
      <div class="tab-row">
        <button class="tab-btn active" id="tab-revenue" onclick="switchTab('revenue', this)">📈 Revenue</button>
        <button class="tab-btn" id="tab-category" onclick="switchTab('category', this)">🏷️ Categories</button>
        <button class="tab-btn" id="tab-item" onclick="switchTab('item', this)">🔍 Item Deep Dive</button>
      </div>

      <!-- Revenue Tab -->
      <div id="tab-panel-revenue">
        <!-- Summary cards -->
        <div class="stat-row" style="margin-bottom:10px;">
          <div class="stat-card card">
            <div class="stat-label">45-Day Revenue</div>
            <div class="stat-value primary" id="total-revenue-val">₹—</div>
          </div>
          <div class="stat-card card">
            <div class="stat-label">Daily Average</div>
            <div class="stat-value" id="avg-daily-rev">₹—</div>
          </div>
        </div>
        <div class="stat-row" style="margin-bottom:10px;">
          <div class="stat-card card">
            <div class="stat-label">Best Day</div>
            <div class="stat-value" id="best-day-val">₹—</div>
          </div>
          <div class="stat-card card">
            <div class="stat-label">Total Units</div>
            <div class="stat-value" id="total-units-val">—</div>
          </div>
        </div>

        <!-- 30-Day trend -->
        <div class="card chart-card">
          <div class="card-title">30-Day Revenue</div>
          <canvas id="trend-chart-30" height="200"></canvas>
        </div>

        <!-- DOW pattern -->
        <div class="card chart-card">
          <div class="card-title">Day-of-Week Pattern</div>
          <canvas id="dow-chart" height="190"></canvas>
        </div>
      </div>

      <!-- Category Tab -->
      <div id="tab-panel-category" style="display:none">
        <div class="card chart-card">
          <div class="card-title">Revenue by Category</div>
          <canvas id="cat-revenue-chart" height="280"></canvas>
        </div>
        <div class="card chart-card">
          <div class="card-title">Units by Category</div>
          <canvas id="cat-qty-chart" height="280"></canvas>
        </div>
      </div>

      <!-- Item Tab -->
      <div id="tab-panel-item" style="display:none">
        <div style="margin-bottom:12px;">
          <select id="item-selector" class="item-select" onchange="loadItemTrend()">
            <option value="">Select an item...</option>
          </select>
        </div>
        <div class="card chart-card" id="item-chart-wrap" style="display:none">
          <div class="card-title" id="item-chart-title">Item Trend</div>
          <canvas id="item-trend-chart" height="200"></canvas>
        </div>
        <div id="item-stats-wrap" style="display:none">
          <div class="stat-row">
            <div class="stat-card card">
              <div class="stat-label">Avg / Day</div>
              <div class="stat-value" id="item-avg">—</div>
            </div>
            <div class="stat-card card">
              <div class="stat-label">Peak Day</div>
              <div class="stat-value" id="item-peak">—</div>
            </div>
          </div>
        </div>
        <div class="empty-state" id="item-empty">
          <div class="empty-state-icon">🔍</div>
          Select an item to view its trend
        </div>
      </div>
    </div>
  `;

  loadRevenueTrendsData();
  loadCategoryData();
  loadItemSelectorOptions();
}

async function loadRevenueTrendsData() {
  const trendData = await API.getRevenueTrend(30);
  if (trendData && trendData.length) {
    renderTrend30(trendData);
    renderSummaryStats(trendData);
    renderDOWChart(trendData);
  }
}

function renderSummaryStats(data) {
  const revenues = data.map(d => d.revenue || d.total_revenue || 0);
  const total = revenues.reduce((a, b) => a + b, 0);
  const avg = total / revenues.length;
  const best = Math.max(...revenues);

  const fmtRev = v => `₹${Math.round(v).toLocaleString('en-IN')}`;

  setIf('total-revenue-val', fmtRev(total));
  setIf('avg-daily-rev', fmtRev(avg));
  setIf('best-day-val', fmtRev(best));
}

function renderTrend30(data) {
  const el = document.getElementById('trend-chart-30');
  if (!el) return;
  destroyChart('trend30');

  const labels = data.map(d => {
    const dt = new Date(d.date + 'T00:00:00');
    return dt.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
  });
  const values = data.map(d => d.revenue || d.total_revenue || 0);

  const ctx = el.getContext('2d');
  _trendsCharts['trend30'] = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        data: values,
        borderColor: '#E8531A',
        backgroundColor: createGradient(ctx, '#E8531A'),
        borderWidth: 2.5, fill: true, tension: 0.4,
        pointRadius: 2, pointBackgroundColor: '#E8531A',
      }]
    },
    options: lineOpts('₹', true)
  });
}

function renderDOWChart(data) {
  const el = document.getElementById('dow-chart');
  if (!el) return;
  destroyChart('dow');

  // Aggregate by day of week
  const DOW_NAMES = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
  const totals = new Array(7).fill(0);
  const counts = new Array(7).fill(0);
  data.forEach(d => {
    const dow = new Date(d.date + 'T00:00:00').getDay();
    totals[dow] += d.revenue || d.total_revenue || 0;
    counts[dow]++;
  });

  // Reorder Mon → Sun
  const reorder = [1,2,3,4,5,6,0];
  const labels = reorder.map(i => DOW_NAMES[i]);
  const avgs = reorder.map(i => counts[i] > 0 ? totals[i] / counts[i] : 0);
  const maxVal = Math.max(...avgs);
  const colors = avgs.map(v => v === maxVal ? '#E8531A' : (v > maxVal * 0.8 ? '#F97316' : '#2E3450'));

  const ctx = el.getContext('2d');
  _trendsCharts['dow'] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        data: avgs,
        backgroundColor: colors,
        borderRadius: 8, borderSkipped: false,
      }]
    },
    options: {
      ...barOpts(),
      scales: {
        ...barOpts().scales,
        y: { ...barOpts().scales.y, ticks: { ...barOpts().scales.y.ticks, callback: v => `₹${(v/1000).toFixed(0)}k` } }
      }
    }
  });
}

async function loadCategoryData() {
  const data = await API.getCategoryTrends();
  if (!data || !data.length) return;

  const sorted = [...data].sort((a, b) => b.revenue - a.revenue);
  const CAT_COLORS = {
    biryani:'#F97316', chicken:'#EF4444', beverage:'#06B6D4',
    bread:'#D97706', dairy:'#A78BFA', other:'#8B90B0',
    starter:'#84CC16', rice:'#F59E0B', ice_cream:'#EC4899',
    seafood:'#6366F1', family_pack:'#E8531A', soup:'#14B8A6', egg:'#FBBF24'
  };
  const labels = sorted.map(d => d.category);
  const colors = labels.map(l => CAT_COLORS[l] || '#8B90B0');

  // Revenue chart
  const revEl = document.getElementById('cat-revenue-chart');
  if (revEl) {
    destroyChart('catRev');
    const ctx = revEl.getContext('2d');
    _trendsCharts['catRev'] = new Chart(ctx, {
      type: 'bar',
      data: {
        labels,
        datasets: [{ data: sorted.map(d => d.revenue), backgroundColor: colors, borderRadius: 6 }]
      },
      options: {
        ...barOpts(),
        indexAxis: 'y',
        scales: {
          x: { grid: { color: '#2E3450' }, ticks: { color: '#8B90B0', callback: v => `₹${(v/1000).toFixed(0)}k` } },
          y: { grid: { display: false }, ticks: { color: '#F0F2FF', font: { size: 11 } } }
        }
      }
    });
  }

  // Qty chart
  const qtyEl = document.getElementById('cat-qty-chart');
  if (qtyEl) {
    destroyChart('catQty');
    const qSorted = [...data].sort((a, b) => b.qty - a.qty);
    const qLabels = qSorted.map(d => d.category);
    const qColors = qLabels.map(l => CAT_COLORS[l] || '#8B90B0');
    const ctx = qtyEl.getContext('2d');
    _trendsCharts['catQty'] = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: qLabels,
        datasets: [{ data: qSorted.map(d => d.qty), backgroundColor: qColors, borderRadius: 6 }]
      },
      options: {
        ...barOpts(),
        indexAxis: 'y',
        scales: {
          x: { grid: { color: '#2E3450' }, ticks: { color: '#8B90B0' } },
          y: { grid: { display: false }, ticks: { color: '#F0F2FF', font: { size: 11 } } }
        }
      }
    });
  }

  // Total units
  const totalUnits = data.reduce((s, d) => s + (d.qty || 0), 0);
  setIf('total-units-val', totalUnits.toLocaleString('en-IN'));
}

async function loadItemSelectorOptions() {
  const items = await API.getAllItems() || [];
  const sel = document.getElementById('item-selector');
  if (!sel) return;
  items.sort((a, b) => (b.avg_qty || 0) - (a.avg_qty || 0));
  items.forEach(item => {
    const opt = document.createElement('option');
    opt.value = item.item_name;
    opt.textContent = item.item_name;
    sel.appendChild(opt);
  });
}

async function loadItemTrend() {
  const sel = document.getElementById('item-selector');
  const item = sel?.value;
  if (!item) return;

  document.getElementById('item-chart-wrap').style.display = 'none';
  document.getElementById('item-stats-wrap').style.display = 'none';
  document.getElementById('item-empty').style.display = 'block';

  destroyChart('itemTrend');

  const data = await API.getItemTrend(item, 30);
  if (!data || !data.length) {
    document.getElementById('item-empty').innerHTML = `
      <div class="empty-state-icon">📉</div>
      No trend data for "${item}".<br>Backend may not support this endpoint yet.`;
    return;
  }

  document.getElementById('item-empty').style.display = 'none';
  document.getElementById('item-chart-wrap').style.display = 'block';
  document.getElementById('item-stats-wrap').style.display = 'block';
  document.getElementById('item-chart-title').textContent = `${item} — 30-Day Trend`;

  const el = document.getElementById('item-trend-chart');
  const ctx = el.getContext('2d');
  const vals = data.map(d => d.qty_sold || 0);
  _trendsCharts['itemTrend'] = new Chart(ctx, {
    type: 'line',
    data: {
      labels: data.map(d => {
        const dt = new Date(d.date + 'T00:00:00');
        return dt.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
      }),
      datasets: [{
        data: vals,
        borderColor: '#06B6D4', fill: true,
        backgroundColor: createGradient(ctx, '#06B6D4'),
        borderWidth: 2, tension: 0.4,
        pointRadius: 2, pointBackgroundColor: '#06B6D4',
      }]
    },
    options: lineOpts('units')
  });

  const avg = vals.filter(v => v > 0).reduce((a, b) => a + b, 0) / vals.filter(v => v > 0).length;
  setIf('item-avg', avg.toFixed(1));
  setIf('item-peak', Math.max(...vals));
}

function switchTab(tab, btn) {
  _activeTab = tab;
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  ['revenue','category','item'].forEach(t => {
    const el = document.getElementById(`tab-panel-${t}`);
    if (el) el.style.display = t === tab ? 'block' : 'none';
  });
}

// ── Chart helpers ──────────────────────────────────────────────────────────────
function createGradient(ctx, color) {
  return (context) => {
    const chart = context.chart;
    const { ctx: c, chartArea } = chart;
    if (!chartArea) return 'transparent';
    const grad = c.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
    grad.addColorStop(0, color + '40');
    grad.addColorStop(1, color + '00');
    return grad;
  };
}

function lineOpts(unit, currency = false) {
  return {
    responsive: true,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: '#1A1D27', borderColor: '#2E3450', borderWidth: 1,
        titleColor: '#F0F2FF', bodyColor: '#8B90B0',
        callbacks: {
          label: (ctx) => currency
            ? ` ₹${Math.round(ctx.parsed.y).toLocaleString('en-IN')}`
            : ` ${ctx.parsed.y} ${unit}`
        }
      }
    },
    scales: {
      x: { grid: { display: false }, ticks: { color: '#8B90B0', font: { size: 10 }, maxTicksLimit: 8 } },
      y: {
        grid: { color: '#2E3450' },
        ticks: {
          color: '#8B90B0', font: { size: 10 },
          callback: currency ? (v => `₹${(v/1000).toFixed(0)}k`) : undefined
        }
      }
    },
    animation: { duration: 700, easing: 'easeOutQuart' }
  };
}

function barOpts() {
  return {
    responsive: true,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: '#1A1D27', borderColor: '#2E3450', borderWidth: 1,
        titleColor: '#F0F2FF', bodyColor: '#8B90B0',
      }
    },
    scales: {
      x: { grid: { color: '#2E3450' }, ticks: { color: '#8B90B0', font: { size: 11 } } },
      y: { grid: { display: false }, ticks: { color: '#F0F2FF', font: { size: 11 } } }
    },
    animation: { duration: 700, easing: 'easeOutQuart' }
  };
}

function destroyChart(key) {
  if (_trendsCharts[key]) {
    _trendsCharts[key].destroy();
    delete _trendsCharts[key];
  }
}

function setIf(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}
