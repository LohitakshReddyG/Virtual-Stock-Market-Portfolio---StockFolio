/* ============================================================
   VIRTUAL STOCK MARKET PORTFOLIO MANAGER — APP.JS
   ============================================================ */

const API = "http://localhost:5000";
let currentUser = null;
let tradeMode = null;      // 'BUY' | 'SELL'
let tradeStock = null;     // { stock_id, stock_name, company_name, current_price }

/* ============================================================
   INIT
   ============================================================ */
window.addEventListener("DOMContentLoaded", () => {
  const saved = localStorage.getItem("stockUser");
  if (saved) {
    currentUser = JSON.parse(saved);
    showDashboard();
  }

  // Set today's date on overview
  const now = new Date();
  const el = document.getElementById("overview-date");
  if (el) el.textContent = now.toLocaleDateString("en-IN", { weekday: "long", year: "numeric", month: "long", day: "numeric" });
});

/* ============================================================
   AUTH TABS
   ============================================================ */
function showTab(tab) {
  document.getElementById("login-form").classList.toggle("hidden", tab !== "login");
  document.getElementById("register-form").classList.toggle("hidden", tab !== "register");
  document.getElementById("tab-login").classList.toggle("active", tab === "login");
  document.getElementById("tab-register").classList.toggle("active", tab === "register");
  clearErrors();
}

function clearErrors() {
  ["login-error", "reg-error", "modal-error"].forEach(id => {
    const el = document.getElementById(id);
    if (el) { el.textContent = ""; el.classList.add("hidden"); }
  });
}

function showError(id, msg) {
  const el = document.getElementById(id);
  el.textContent = msg;
  el.classList.remove("hidden");
}

/* ============================================================
   REGISTER
   ============================================================ */
async function handleRegister(e) {
  e.preventDefault();
  clearErrors();
  const btn = document.getElementById("reg-btn");
  btn.disabled = true;
  btn.textContent = "Creating account...";

  const name = document.getElementById("reg-name").value.trim();
  const phone = document.getElementById("reg-phone").value.trim();
  const email = document.getElementById("reg-email").value.trim();
  const password = document.getElementById("reg-password").value;

  try {
    const res = await fetch(`${API}/api/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, phone, email, password })
    });
    const data = await res.json();
    if (!res.ok) { showError("reg-error", data.error || "Registration failed"); return; }

    currentUser = data.user;
    localStorage.setItem("stockUser", JSON.stringify(currentUser));
    showDashboard();
    showToast(`Welcome, ${currentUser.name}! Add funds to start trading.`, "success");
  } catch (err) {
    showError("reg-error", "Server error. Make sure Flask is running.");
  } finally {
    btn.disabled = false;
    btn.textContent = "Create Account";
  }
}

/* ============================================================
   LOGIN
   ============================================================ */
async function handleLogin(e) {
  e.preventDefault();
  clearErrors();
  const btn = document.getElementById("login-btn");
  btn.disabled = true;
  btn.textContent = "Logging in...";

  const email = document.getElementById("login-email").value.trim();
  const password = document.getElementById("login-password").value;

  try {
    const res = await fetch(`${API}/api/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });
    const data = await res.json();
    if (!res.ok) { showError("login-error", data.error || "Login failed"); return; }

    currentUser = data.user;
    localStorage.setItem("stockUser", JSON.stringify(currentUser));
    showDashboard();
    showToast(`Welcome back, ${currentUser.name}!`, "success");
  } catch (err) {
    showError("login-error", "Server error. Make sure Flask is running.");
  } finally {
    btn.disabled = false;
    btn.textContent = "Login";
  }
}

/* ============================================================
   LOGOUT
   ============================================================ */
function logout() {
  currentUser = null;
  localStorage.removeItem("stockUser");
  document.getElementById("dashboard").classList.add("hidden");
  document.getElementById("auth-screen").classList.remove("hidden");
  showTab("login");
}

/* ============================================================
   SHOW DASHBOARD
   ============================================================ */
function showDashboard() {
  document.getElementById("auth-screen").classList.add("hidden");
  document.getElementById("dashboard").classList.remove("hidden");
  updateSidebar();
  showPage("overview");
}

function updateSidebar() {
  if (!currentUser) return;
  document.getElementById("sidebar-name").textContent = currentUser.name;
  document.getElementById("sidebar-balance").textContent = formatCurrency(currentUser.balance);
  document.getElementById("sidebar-avatar").textContent = currentUser.name.charAt(0).toUpperCase();
}

async function refreshUserBalance() {
  try {
    const res = await fetch(`${API}/api/user/${currentUser.user_id}`);
    const user = await res.json();
    if (res.ok) {
      currentUser.balance = user.balance;
      localStorage.setItem("stockUser", JSON.stringify(currentUser));
      updateSidebar();
      document.getElementById("stat-balance").textContent = formatCurrency(user.balance);
    }
  } catch (_) {}
}

/* ============================================================
   PAGE NAVIGATION
   ============================================================ */
function showPage(page) {
  // Hide all pages
  document.querySelectorAll(".page").forEach(p => p.classList.add("hidden"));
  document.querySelectorAll(".nav-link").forEach(n => n.classList.remove("active"));

  document.getElementById(`page-${page}`).classList.remove("hidden");
  document.getElementById(`nav-${page}`).classList.add("active");

  // Load data for the page
  if (page === "overview")     loadOverview();
  if (page === "market")       loadMarket();
  if (page === "portfolio")    loadPortfolio();
  if (page === "transactions") loadTransactions();
}

/* ============================================================
   OVERVIEW
   ============================================================ */
async function loadOverview() {
  await refreshUserBalance();

  // Load portfolio stats
  try {
    const res = await fetch(`${API}/api/portfolio/${currentUser.user_id}`);
    const data = await res.json();
    if (res.ok) {
      document.getElementById("stat-portfolio-value").textContent = formatCurrency(data.total_current_value);
      const pl = data.total_profit_loss;
      const plEl = document.getElementById("stat-pl");
      plEl.textContent = (pl >= 0 ? "+" : "") + formatCurrency(pl);
      plEl.className = "stat-value " + (pl >= 0 ? "pl-pos" : "pl-neg");
      const card = document.getElementById("stat-pl-card");
      card.className = "stat-card " + (pl >= 0 ? "accent-green" : "accent-red");
      document.getElementById("stat-stocks-owned").textContent = data.holdings.length;
    }
  } catch (_) {}

  // Load recent transactions
  try {
    const res = await fetch(`${API}/api/transactions/${currentUser.user_id}`);
    const txns = await res.json();
    const container = document.getElementById("overview-txn-table");
    if (!res.ok || !txns.length) {
      container.innerHTML = '<p class="empty-msg">No transactions yet. Buy a stock to get started!</p>';
      return;
    }
    const recent = txns.slice(0, 5);
    container.innerHTML = renderTransactionTable(recent);
  } catch (_) {}
}

/* ============================================================
   MARKET
   ============================================================ */
async function loadMarket() {
  const loading = document.getElementById("market-loading");
  const tableWrap = document.getElementById("market-table");
  loading.classList.remove("hidden");
  tableWrap.classList.add("hidden");

  try {
    const res = await fetch(`${API}/api/stocks`);
    const stocks = await res.json();
    loading.classList.add("hidden");

    if (!stocks.length) {
      tableWrap.innerHTML = '<p class="empty-msg">No stocks found in database.</p>';
      tableWrap.classList.remove("hidden");
      return;
    }

    tableWrap.innerHTML = `
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Ticker</th>
            <th>Company</th>
            <th>Sector</th>
            <th>Price (₹)</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          ${stocks.map((s, i) => `
            <tr>
              <td>${i + 1}</td>
              <td><strong style="color:var(--accent-blue)">${esc(s.stock_name)}</strong></td>
              <td>${esc(s.company_name || s.stock_name)}</td>
              <td><span style="color:var(--text-secondary)">${esc(s.sector || "—")}</span></td>
              <td><strong>${formatCurrency(s.current_price)}</strong></td>
              <td>
                <button class="btn-buy"  onclick="openTradeModal('BUY',  ${JSON.stringify(s).replace(/"/g,'&quot;')})">Buy</button>
                <button class="btn-sell" onclick="openTradeModal('SELL', ${JSON.stringify(s).replace(/"/g,'&quot;')})">Sell</button>
              </td>
            </tr>
          `).join("")}
        </tbody>
      </table>`;
    tableWrap.classList.remove("hidden");
  } catch (err) {
    loading.textContent = "❌ Failed to load stocks. Is Flask running?";
  }
}

/* ============================================================
   PORTFOLIO
   ============================================================ */
async function loadPortfolio() {
  const tableWrap = document.getElementById("portfolio-table");
  const statsDiv  = document.getElementById("portfolio-stats");

  try {
    const res = await fetch(`${API}/api/portfolio/${currentUser.user_id}`);
    const data = await res.json();
    if (!res.ok) { tableWrap.innerHTML = '<p class="empty-msg">Could not load portfolio.</p>'; return; }

    const pl = data.total_profit_loss;
    statsDiv.innerHTML = `
      <div class="stat-card accent-purple">
        <div class="stat-label">Total Invested</div>
        <div class="stat-value">${formatCurrency(data.total_invested)}</div>
      </div>
      <div class="stat-card accent-blue">
        <div class="stat-label">Current Value</div>
        <div class="stat-value">${formatCurrency(data.total_current_value)}</div>
      </div>
      <div class="stat-card ${pl >= 0 ? 'accent-green' : 'accent-red'}">
        <div class="stat-label">Total P&L</div>
        <div class="stat-value ${pl >= 0 ? 'pl-pos' : 'pl-neg'}">${(pl >= 0 ? "+" : "") + formatCurrency(pl)}</div>
      </div>`;

    if (!data.holdings.length) {
      tableWrap.innerHTML = '<p class="empty-msg">Your portfolio is empty. Go to Market to buy stocks!</p>';
      return;
    }

    tableWrap.innerHTML = `
      <table>
        <thead>
          <tr>
            <th>Stock</th>
            <th>Shares</th>
            <th>Avg Buy Price</th>
            <th>Current Price</th>
            <th>Invested</th>
            <th>Current Value</th>
            <th>P&L</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          ${data.holdings.map(h => {
            const pl = h.profit_loss;
            return `<tr>
              <td>
                <strong style="color:var(--accent-blue)">${esc(h.stock_name)}</strong><br>
                <span style="font-size:0.78rem;color:var(--text-secondary)">${esc(h.company_name || "")}</span>
              </td>
              <td>${h.shares_owned}</td>
              <td>${formatCurrency(h.avg_buy_price)}</td>
              <td>${formatCurrency(h.current_price)}</td>
              <td>${formatCurrency(h.total_invested)}</td>
              <td>${formatCurrency(h.current_value)}</td>
              <td class="${pl >= 0 ? 'pl-pos' : 'pl-neg'}">${(pl >= 0 ? "+" : "") + formatCurrency(pl)}</td>
              <td>
                <button class="btn-sell" onclick="openTradeModal('SELL', ${JSON.stringify(h).replace(/"/g,'&quot;')})">Sell</button>
              </td>
            </tr>`;
          }).join("")}
        </tbody>
      </table>`;
  } catch (_) {
    tableWrap.innerHTML = '<p class="empty-msg">Error loading portfolio.</p>';
  }
}

/* ============================================================
   TRANSACTIONS
   ============================================================ */
async function loadTransactions() {
  const container = document.getElementById("transaction-table");
  try {
    const res = await fetch(`${API}/api/transactions/${currentUser.user_id}`);
    const txns = await res.json();
    if (!res.ok || !txns.length) {
      container.innerHTML = '<p class="empty-msg">No transactions yet.</p>';
      return;
    }
    container.innerHTML = renderTransactionTable(txns);
  } catch (_) {
    container.innerHTML = '<p class="empty-msg">Error loading transactions.</p>';
  }
}

function renderTransactionTable(txns) {
  return `
    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>Type</th>
          <th>Stock</th>
          <th>Qty</th>
          <th>Price/Share</th>
          <th>Total</th>
          <th>Date</th>
          <th>Time</th>
        </tr>
      </thead>
      <tbody>
        ${txns.map((t, i) => `
          <tr>
            <td>${t.transaction_id}</td>
            <td><span class="badge badge-${t.transaction_type.toLowerCase()}">${t.transaction_type}</span></td>
            <td><strong>${esc(t.stock_name)}</strong></td>
            <td>${t.quantity}</td>
            <td>${formatCurrency(t.price_per_share)}</td>
            <td><strong>${formatCurrency(t.total_amount)}</strong></td>
            <td>${t.transaction_date}</td>
            <td>${t.transaction_time}</td>
          </tr>`).join("")}
      </tbody>
    </table>`;
}

/* ============================================================
   TRADE MODAL
   ============================================================ */
function openTradeModal(mode, stock) {
  tradeMode  = mode;
  tradeStock = stock;
  clearErrors();

  document.getElementById("modal-title").textContent     = `${mode} ${stock.stock_name}`;
  document.getElementById("modal-stock-name").textContent = stock.stock_name;
  document.getElementById("modal-company-name").textContent = stock.company_name || "";
  document.getElementById("modal-price").textContent     = formatCurrency(stock.current_price);
  document.getElementById("trade-qty").value = 1;
  updateModalTotal();

  const btn = document.getElementById("modal-confirm-btn");
  btn.textContent = mode === "BUY" ? "✅ Confirm Buy" : "📤 Confirm Sell";
  btn.style.background = mode === "BUY"
    ? "linear-gradient(135deg, #22c55e, #16a34a)"
    : "linear-gradient(135deg, #ef4444, #dc2626)";

  document.getElementById("trade-modal").classList.remove("hidden");
  document.getElementById("trade-qty").focus();
}

document.addEventListener("DOMContentLoaded", () => {
  const qtyInput = document.getElementById("trade-qty");
  if (qtyInput) qtyInput.addEventListener("input", updateModalTotal);
});

function updateModalTotal() {
  const qty = parseInt(document.getElementById("trade-qty").value) || 0;
  const price = tradeStock ? parseFloat(tradeStock.current_price) : 0;
  document.getElementById("modal-total").textContent = formatCurrency(qty * price);
}

function closeTradeModal() {
  document.getElementById("trade-modal").classList.add("hidden");
  tradeMode = null;
  tradeStock = null;
}

function closeModal(e) {
  if (e.target.id === "trade-modal") closeTradeModal();
}

async function confirmTrade() {
  if (!tradeMode || !tradeStock) return;
  clearErrors();
  const qty = parseInt(document.getElementById("trade-qty").value);
  if (!qty || qty <= 0) { showError("modal-error", "Please enter a valid quantity."); return; }

  const btn = document.getElementById("modal-confirm-btn");
  btn.disabled = true;
  btn.textContent = "Processing...";

  const endpoint = tradeMode === "BUY" ? "/api/buy" : "/api/sell";
  try {
    const res = await fetch(`${API}${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: currentUser.user_id, stock_id: tradeStock.stock_id, quantity: qty })
    });
    const data = await res.json();
    if (!res.ok) { showError("modal-error", data.error || "Trade failed"); return; }

    closeTradeModal();
    const emoji = tradeMode === "BUY" ? "🟢" : "🔴";
    showToast(`${emoji} ${data.message} | Total: ${formatCurrency(data.total_cost || data.total_received)}`, "success");
    await refreshUserBalance();

    // Refresh whichever page is visible
    const activePage = document.querySelector(".page:not(.hidden)");
    if (activePage?.id === "page-market")       loadMarket();
    if (activePage?.id === "page-portfolio")    loadPortfolio();
    if (activePage?.id === "page-transactions") loadTransactions();
    if (activePage?.id === "page-overview")     loadOverview();
  } catch (_) {
    showError("modal-error", "Server error. Please try again.");
  } finally {
    btn.disabled = false;
    btn.textContent = tradeMode === "BUY" ? "✅ Confirm Buy" : "📤 Confirm Sell";
  }
}

/* ============================================================
   DEPOSIT MODAL
   ============================================================ */
function openDepositModal() {
  document.getElementById("deposit-amount").value = "";
  const errEl = document.getElementById("deposit-error");
  errEl.textContent = ""; errEl.classList.add("hidden");
  document.getElementById("deposit-modal").classList.remove("hidden");
  document.getElementById("deposit-amount").focus();
}

function closeDepositModal() {
  document.getElementById("deposit-modal").classList.add("hidden");
}

function closeDepositModalOverlay(e) {
  if (e.target.id === "deposit-modal") closeDepositModal();
}

function setDepositAmount(amount) {
  document.getElementById("deposit-amount").value = amount;
  const errEl = document.getElementById("deposit-error");
  errEl.textContent = ""; errEl.classList.add("hidden");
}

async function confirmDeposit() {
  const amountRaw = document.getElementById("deposit-amount").value;
  const amount = parseFloat(amountRaw);
  const errEl = document.getElementById("deposit-error");
  errEl.textContent = ""; errEl.classList.add("hidden");

  if (!amountRaw || isNaN(amount) || amount <= 0) {
    errEl.textContent = "Please enter a valid amount greater than ₹0.";
    errEl.classList.remove("hidden");
    return;
  }
  if (amount > 1_000_000) {
    errEl.textContent = "Maximum deposit per transaction is ₹10,00,000.";
    errEl.classList.remove("hidden");
    return;
  }

  const btn = document.getElementById("deposit-confirm-btn");
  btn.disabled = true;
  btn.textContent = "Processing...";

  try {
    const res = await fetch(`${API}/api/user/${currentUser.user_id}/deposit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ amount })
    });
    const data = await res.json();
    if (!res.ok) {
      errEl.textContent = data.error || "Deposit failed. Please try again.";
      errEl.classList.remove("hidden");
      return;
    }
    // Update balance everywhere
    currentUser.balance = data.balance;
    localStorage.setItem("stockUser", JSON.stringify(currentUser));
    updateSidebar();
    document.getElementById("stat-balance").textContent = formatCurrency(data.balance);
    closeDepositModal();
    showToast(`💰 ₹${parseFloat(amount).toLocaleString("en-IN")} added to your balance!`, "success");
  } catch (_) {
    errEl.textContent = "Server error. Please try again.";
    errEl.classList.remove("hidden");
  } finally {
    btn.disabled = false;
    btn.textContent = "✅ Confirm Deposit";
  }
}

/* ============================================================
   UTILITY
   ============================================================ */
function formatCurrency(val) {
  const n = parseFloat(val) || 0;
  return "₹" + n.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function esc(str) {
  if (!str) return "";
  return String(str).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}

function showToast(msg, type = "success") {
  const toast = document.getElementById("toast");
  toast.textContent = msg;
  toast.className = `toast ${type}`;
  toast.classList.remove("hidden");
  setTimeout(() => toast.classList.add("hidden"), 4000);
}
