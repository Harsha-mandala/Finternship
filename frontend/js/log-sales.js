/* ═══════════════════════════════════════════════════════════
   log-sales.js — Screen 3
   ═══════════════════════════════════════════════════════════ */

let _allItems = [];
let _logDate = null;

function renderLogSales(container) {
  const today = new Date().toISOString().split('T')[0];
  _logDate = today;

  container.innerHTML = `
    <div class="screen">
      <!-- Header row -->
      <div class="screen-title-row">
        <div class="screen-title">Log Sales</div>
        <input type="date" id="log-date" class="input-field" value="${today}"
               style="max-width:150px; font-size:13px; padding:8px 10px;">
      </div>

      <!-- Info card -->
      <div class="card" style="padding:12px 14px; margin-bottom:12px; font-size:13px; color:var(--color-text-muted); line-height:1.5;">
        Enter how many units of each item were sold today. Only fill items actually sold.
      </div>

      <!-- Search -->
      <div class="search-row">
        <input type="text" id="item-search" class="input-field"
               placeholder="🔍 Search items...">
      </div>

      <!-- Category filter tabs -->
      <div class="tab-row" id="cat-tabs" style="margin-bottom:12px;">
        <button class="tab-btn active" onclick="filterCat('all', this)">All</button>
        <button class="tab-btn" onclick="filterCat('biryani', this)">🍛 Biryani</button>
        <button class="tab-btn" onclick="filterCat('chicken', this)">🍗 Chicken</button>
        <button class="tab-btn" onclick="filterCat('beverage', this)">🥤 Beverages</button>
        <button class="tab-btn" onclick="filterCat('bread', this)">🫓 Breads</button>
        <button class="tab-btn" onclick="filterCat('dairy', this)">🧀 Dairy</button>
        <button class="tab-btn" onclick="filterCat('starter', this)">🍟 Starters</button>
        <button class="tab-btn" onclick="filterCat('rice', this)">🍚 Rice</button>
        <button class="tab-btn" onclick="filterCat('ice_cream', this)">🍦 Ice Cream</button>
      </div>

      <!-- Items form -->
      <div id="sales-form" class="sales-form-wrap">
        <div class="loading-spinner"></div>
      </div>

      <!-- Save Button -->
      <div class="sticky-footer">
        <button class="btn btn-primary btn-full" id="save-sales-btn" onclick="saveSales()">
          💾 Save Sales Data
        </button>
      </div>
    </div>
  `;

  // Event listeners
  document.getElementById('log-date').addEventListener('change', (e) => {
    _logDate = e.target.value;
    loadSalesForm(e.target.value);
  });

  document.getElementById('item-search').addEventListener('input', (e) => {
    const q = e.target.value.toLowerCase();
    document.querySelectorAll('.sales-item-row').forEach(row => {
      const name = row.dataset.item?.toLowerCase() || '';
      const cat  = row.dataset.cat?.toLowerCase() || '';
      row.style.display = name.includes(q) || cat.includes(q) ? 'flex' : 'none';
    });
  });

  loadSalesForm(today);
}

async function loadSalesForm(date) {
  const formEl = document.getElementById('sales-form');
  if (!formEl) return;
  formEl.innerHTML = '<div class="loading-spinner"></div>';

  // Load items list
  let items = _allItems;
  if (!items.length) {
    items = await API.getAllItems() || [];
    _allItems = items;
  }

  // Load existing sales for this date
  const existing = await API.getSalesByDate(date) || [];
  const existingMap = {};
  existing.forEach(s => existingMap[s.item_name] = s.qty_sold);

  // Sort: existing sales first, then by avg_qty desc
  items.sort((a, b) => {
    const aHas = existingMap[a.item_name] ? 1 : 0;
    const bHas = existingMap[b.item_name] ? 1 : 0;
    if (aHas !== bHas) return bHas - aHas;
    return (b.avg_qty || 0) - (a.avg_qty || 0);
  });

  if (!items.length) {
    formEl.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">📋</div>
        No items found. Check if the backend is running.
      </div>`;
    return;
  }

  const rows = items.map(item => {
    const val = existingMap[item.item_name] || 0;
    const cat = item.category || 'other';
    return `
      <div class="sales-item-row" data-item="${item.item_name}" data-cat="${cat}">
        <div class="sales-item-name">${item.item_name}</div>
        <div class="qty-stepper compact">
          <button class="stepper-btn sm" onclick="adjustQty(this, -1)">−</button>
          <input type="number" class="qty-input" data-item="${item.item_name}"
                 value="${val}" min="0" step="1">
          <button class="stepper-btn sm" onclick="adjustQty(this, 1)">+</button>
        </div>
      </div>`;
  }).join('');

  formEl.innerHTML = rows;
}

function adjustQty(btn, delta) {
  // Find input: if minus btn, next sibling is input; if plus btn, previous
  const input = delta === -1 ? btn.nextElementSibling : btn.previousElementSibling;
  if (!input) return;
  const val = Math.max(0, (parseInt(input.value) || 0) + delta);
  input.value = val;
  // Highlight if > 0
  input.style.borderColor = val > 0 ? 'var(--color-primary)' : '';
  input.style.color = val > 0 ? 'var(--color-primary)' : '';
}

function filterCat(cat, btn) {
  // Update tab UI
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');

  // Filter rows
  document.querySelectorAll('.sales-item-row').forEach(row => {
    if (cat === 'all' || row.dataset.cat === cat) {
      row.style.display = 'flex';
    } else {
      row.style.display = 'none';
    }
  });
}

async function saveSales() {
  const btn = document.getElementById('save-sales-btn');
  const date = document.getElementById('log-date')?.value || _logDate;

  // Collect all non-zero entries
  const inputs = document.querySelectorAll('.qty-input');
  const entries = [];
  inputs.forEach(input => {
    const qty = parseInt(input.value) || 0;
    if (qty > 0) {
      entries.push({
        date,
        item_name: input.dataset.item,
        qty_sold: qty
      });
    }
  });

  if (entries.length === 0) {
    showToast('No quantities entered!', 'error');
    return;
  }

  btn.disabled = true;
  btn.textContent = '⏳ Saving...';

  const result = await API.logSales({ date, entries });

  if (result) {
    btn.textContent = '✅ Saved!';
    btn.classList.remove('btn-primary');
    btn.classList.add('btn-success');
    showToast(`Saved ${entries.length} items for ${date}`, 'success');

    setTimeout(() => {
      btn.disabled = false;
      btn.textContent = '💾 Save Sales Data';
      btn.classList.remove('btn-success');
      btn.classList.add('btn-primary');
    }, 2500);
  } else {
    btn.disabled = false;
    btn.textContent = '💾 Save Sales Data';
    showToast('Backend offline — data not saved', 'error');
  }
}
