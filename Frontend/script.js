// ----- API Utility -----

function redirectToLogin() {
    window.location.href = '/login.html';
}

function never() {
    // Used after redirect to stop further rendering in this script execution.
    return new Promise(() => {});
}

function toNumber(value, fallback = 0) {
    const n = Number(value);
    return Number.isFinite(n) ? n : fallback;
}

function toText(value, fallback = '') {
    if (value === null || value === undefined) return fallback;
    return String(value);
}

function toColor(value, fallback = '#999') {
    const s = toText(value, '').trim();
    return s ? s : fallback;
}

async function fetchWithFallback(url, fallbackData, options = {}) {
    try {
        const res = await fetch(url, {
            credentials: 'include',
            ...options
        });
        if (res.status === 401 || res.status === 403) {
            redirectToLogin();
            return await never();
        }
        if (!res.ok) throw new Error('API error');
        return await res.json();
    } catch (err) {
        console.warn(`API unavailable (${url}), using mock data`);
        return fallbackData;
    }
}

async function postJson(url, data) {
    return fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(data)
    });
}

async function putJson(url, data) {
    return fetch(url, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(data)
    });
}

// ----- Mock Data (fallback) -----

const MOCK_SUBSCRIPTIONS = [
    { name: "Crunchyroll", icon: "📺", amount: 7.99, date: "Feb 15" }
];

const MOCK_TRANSACTIONS = [
    { name: "Kroger", icon: "🛒", amount: 45.20 },
    { name: "Taco Bell", icon: "🌮", amount: 12.85 },
    { name: "Chic-fil-a", icon: "🍔", amount: 15.40 },
    { name: "Starbucks", icon: "☕", amount: 6.50 },
    { name: "Gas Station", icon: "⛽", amount: 40.00 }
];

const MOCK_CATEGORIES = [
    { name: "Rent", amount: 1200, color: "#4CAF50" },
    { name: "Food", amount: 400, color: "#FF9800" },
    { name: "Bills", amount: 250, color: "#2196F3" },
    { name: "Fun", amount: 150, color: "#E91E63" }
];

const MOCK_GOALS = [
    { name: "Japan 2030", date: "Jan 2030", monthly: 100, total: 12000 }
];

const MOCK_BUDGET = { spent: 119.95, limit: 3000 };

// ----- State -----

let spent = 0;
let limit = 3000;
let subscriptionData = [];
let dailyTransactions = [];
let spendingCategories = [];
let goals = [];
let isConnected = false;

async function requireAuth() {
    try {
        const res = await fetch('/api/v1/auth/me', { credentials: 'include' });
        if (res.status === 401 || res.status === 403) {
            redirectToLogin();
            return await never();
        }
        // If API is down or errors, allow demo fallback behavior.
        return;
    } catch {
        return;
    }
}

// ----- Budget -----

function updateBudgetUI() {
    const safeLimit = toNumber(limit, 0);
    const safeSpent = toNumber(spent, 0);
    const percentage =
        safeLimit > 0 ? Math.min((safeSpent / safeLimit) * 100, 100).toFixed(0) : '0';
    
    const budgetLimitEl = document.getElementById('budget-limit');
    const progressTextEl = document.getElementById('progress-text');
    const spentAmountEl = document.getElementById('spent-amount');
    const progressBarEl = document.getElementById('progress-bar');
    
    if (budgetLimitEl) budgetLimitEl.innerText = safeLimit;
    if (progressTextEl) progressTextEl.innerText = `${percentage}%`;
    if (spentAmountEl) spentAmountEl.innerText = safeSpent.toFixed(2);
    if (progressBarEl) {
        progressBarEl.style.width = `${percentage}%`;
        progressBarEl.style.backgroundColor = percentage >= 100 ? "#ff4d4d" : "#4CAF50";
    }
}

async function loadBudget() {
    const data = await fetchWithFallback('/api/v1/budget', MOCK_BUDGET);
    spent = toNumber(data?.spent, 0);
    limit = toNumber(data?.limit, 3000);
    updateBudgetUI();
}

async function updateBudget() {
    const newLimitEl = document.getElementById('new-limit');
    const newLimit = parseInt(newLimitEl.value);
    
    if (newLimit >= 0) {
        try {
            const res = await putJson('/api/v1/budget', { limit: newLimit });
            if (res.ok) {
                const data = await res.json();
                limit = toNumber(data?.limit, newLimit);
                spent = toNumber(data?.spent, spent);
            } else {
                // Fallback to local update
                limit = newLimit;
            }
        } catch {
            limit = newLimit;
        }
        updateBudgetUI();
        toggleEdit();
    }
}

function toggleEdit() {
    const div = document.getElementById('edit-fields');
    if (div) {
        div.style.display = div.style.display === 'none' ? 'block' : 'none';
    }
}

// ----- Subscriptions -----

function createSubscriptionRow(name, icon, amount, date) {
    const div = document.createElement('div');
    div.className = 'sub-row';
    
    const nameSpan = document.createElement('span');
    nameSpan.className = 'sub-name';
    nameSpan.textContent = name;
    
    const iconSpan = document.createElement('span');
    iconSpan.className = 'sub-icon';
    iconSpan.textContent = icon;
    
    const amountSpan = document.createElement('span');
    amountSpan.className = 'sub-amount';
    amountSpan.textContent = amount;
    
    const dateSpan = document.createElement('span');
    dateSpan.className = 'sub-date';
    dateSpan.textContent = date;
    
    div.appendChild(nameSpan);
    div.appendChild(iconSpan);
    div.appendChild(amountSpan);
    div.appendChild(dateSpan);
    
    return div;
}

function renderSubscriptionsUI() {
    const container = document.getElementById('subscription-list');
    if (!container) return;
    
    container.innerHTML = '';
    
    subscriptionData.forEach(sub => {
        const amount = toNumber(sub?.amount, 0);
        const row = createSubscriptionRow(
            toText(sub?.name, 'Unknown'),
            toText(sub?.icon, '💳'),
            `$${amount.toFixed(2)}`,
            toText(sub?.date, '')
        );
        container.appendChild(row);
    });
    
    // Render placeholder rows (up to 4 total)
    const emptyCount = Math.max(0, 4 - subscriptionData.length);
    for (let i = 0; i < emptyCount; i++) {
        const emptyRow = createSubscriptionRow('', '', '', '');
        emptyRow.classList.add('empty');
        container.appendChild(emptyRow);
    }
}

async function loadSubscriptions() {
    const data = await fetchWithFallback('/api/v1/subscriptions', MOCK_SUBSCRIPTIONS);
    subscriptionData = Array.isArray(data) ? data : [];
    renderSubscriptionsUI();
}

// ----- Daily Spending -----

function renderSpendingUI() {
    const container = document.getElementById('transaction-history');
    if (!container) return;
    
    let total = 0;
    container.innerHTML = '';
    
    dailyTransactions.forEach(item => {
        const amount = toNumber(item?.amount, 0);
        total += amount;
        
        const row = document.createElement('div');
        row.className = 'spending-row';
        
        const nameSpan = document.createElement('span');
        nameSpan.className = 'spending-name';
        nameSpan.textContent = toText(item?.name, 'Unknown');
        
        const iconSpan = document.createElement('span');
        iconSpan.className = 'spending-icon';
        iconSpan.textContent = toText(item?.icon, '💳');
        
        const amountSpan = document.createElement('span');
        amountSpan.className = 'spending-amount';
        amountSpan.textContent = `$${amount.toFixed(2)}`;
        
        row.appendChild(nameSpan);
        row.appendChild(iconSpan);
        row.appendChild(amountSpan);
        container.appendChild(row);
    });
    
    const dailyTotalEl = document.getElementById('daily-total');
    if (dailyTotalEl) {
        dailyTotalEl.innerText = `$${total.toFixed(2)}`;
    }
}

async function loadDailySpending() {
    const data = await fetchWithFallback('/api/v1/spending/daily', MOCK_TRANSACTIONS);
    dailyTransactions = Array.isArray(data) ? data : [];
    renderSpendingUI();
}

// ----- Spending Chart -----

function updateChartUI() {
    const chart = document.getElementById('spending-chart');
    const legend = document.getElementById('chart-legend');
    const totalDisplay = document.getElementById('total-spent-display');
    
    if (!chart || !legend || !totalDisplay) return;
    
    const total = spendingCategories.reduce((sum, cat) => sum + toNumber(cat?.amount, 0), 0);
    totalDisplay.innerText = `$${total.toFixed(2)}`;
    
    if (total === 0) {
        chart.style.background = `conic-gradient(#eee 0% 100%)`;
        legend.innerHTML = '';
        return;
    }
    
    let gradientString = "";
    let cumulativePercent = 0;
    
    legend.innerHTML = "";
    
    spendingCategories.forEach((cat, index) => {
        const amount = toNumber(cat?.amount, 0);
        const percent = (amount / total) * 100;
        const start = cumulativePercent;
        cumulativePercent += percent;
        
        const color = toColor(cat?.color, '#999');
        gradientString += `${color} ${start}% ${cumulativePercent}%`;
        if (index < spendingCategories.length - 1) gradientString += ", ";
        
        const item = document.createElement('div');
        item.className = 'legend-item';
        
        const dot = document.createElement('span');
        dot.className = 'dot';
        dot.style.background = color;
        
        const label = document.createElement('span');
        label.textContent = `${toText(cat?.name, 'Unknown')}: $${amount.toFixed(2)}`;
        
        item.appendChild(dot);
        item.appendChild(label);
        legend.appendChild(item);
    });
    
    chart.style.background = `conic-gradient(${gradientString})`;
}

async function loadCategories() {
    const data = await fetchWithFallback('/api/v1/spending/categories', MOCK_CATEGORIES);
    spendingCategories = Array.isArray(data) ? data : [];
    updateChartUI();
}

// ----- Goals -----

function renderGoalsUI() {
    const list = document.getElementById('goals-list');
    if (!list) return;
    
    list.innerHTML = '';
    
    goals.forEach((goal, index) => {
        const name = toText(goal?.name, 'Untitled goal');
        const monthly = toNumber(goal?.monthly, 0);
        const total = toNumber(goal?.total, 0);

        const div = document.createElement('div');
        div.className = 'goal-item';
        
        div.innerHTML = `
            <div class="goal-info">
                <span class="goal-name">${name}</span>
                <div class="goal-amounts">
                    <span class="monthly-rate">$${monthly}/m</span>
                    <span class="total-target">Target: $${total}</span>
                </div>
            </div>
            <div class="goal-actions">
                <button class="edit-goal-btn" onclick="editGoal(${index})">✎</button>
                <button class="delete-goal-btn" onclick="deleteGoal(${index})">×</button>
            </div>
        `;
        
        list.appendChild(div);
    });
}

function deleteGoal(index) {
    if (confirm("Are you sure you want to delete this goal?")) {
        goals.splice(index, 1); // Remove the goal from the array
        renderGoalsUI();        // Refresh the list
    }
}

function editGoal(index) {
    const goal = goals[index];
    
    // Fill the modal fields with existing data
    document.getElementById('goal-name').value = toText(goal?.name, '');
    document.getElementById('goal-monthly').value = toText(goal?.monthly, '');
    document.getElementById('goal-total').value = toText(goal?.total, '');
    // Note: goal.date handling depends on your specific date format
    
    openModal();
    
    // Remove the old version once they hit "Save" (updated in saveGoal)
    goals.splice(index, 1);
}

async function loadGoals() {
    const data = await fetchWithFallback('/api/v1/goals', MOCK_GOALS);
    goals = Array.isArray(data) ? data : [];
    renderGoalsUI();
}

function openModal() {
    const modal = document.getElementById('goal-modal');
    if (modal) modal.style.display = 'flex';
}

function closeModal() {
    const modal = document.getElementById('goal-modal');
    if (modal) modal.style.display = 'none';
}

async function saveGoal() {
    const name = document.getElementById('goal-name').value;
    const dateValue = document.getElementById('goal-date').value;
    const monthly = parseFloat(document.getElementById('goal-monthly').value);
    const total = parseFloat(document.getElementById('goal-total').value);
    
    if (name && dateValue && monthly && total) {
        const [year, month] = dateValue.split('-');
        const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                           'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const formattedDate = `${monthNames[parseInt(month) - 1]} ${year}`;
        
        const goalData = { name, date: formattedDate, monthly, total };
        
        try {
            const res = await postJson('/api/v1/goals', goalData);
            if (res.ok) {
                const newGoal = await res.json();
                goals.push(newGoal);
            } else {
                goals.push(goalData);
            }
        } catch {
            goals.push(goalData);
        }
        
        renderGoalsUI();
        closeModal();
        
        document.getElementById('goal-name').value = '';
        document.getElementById('goal-date').value = '';
        document.getElementById('goal-monthly').value = '';
        document.getElementById('goal-total').value = '';
    }
}

// ----- Plaid Connection -----

async function checkPlaidStatus() {
    try {
        const res = await fetch('/api/v1/plaid/status', { credentials: 'include' });
        if (res.status === 401 || res.status === 403) {
            redirectToLogin();
            return await never();
        }
        if (res.ok) {
            const data = await res.json();
            isConnected = data.connected;
            updateConnectionUI();
        }
    } catch {
        isConnected = false;
        updateConnectionUI();
    }
}

function updateConnectionUI() {
    const btn = document.getElementById('connect-bank-btn');
    const status = document.getElementById('connection-status');
    
    if (btn) {
        btn.innerText = isConnected ? 'Disconnect Bank' : 'Connect Bank';
        btn.onclick = isConnected ? disconnectBank : connectBank;
    }
    
    if (status) {
        status.innerText = isConnected ? 'Connected' : 'Not connected';
        status.style.color = isConnected ? '#4CAF50' : '#888';
    }
}

async function connectBank() {
    try {
        const res = await postJson('/api/v1/plaid/connect', {});
        if (res.status === 401 || res.status === 403) {
            redirectToLogin();
            return await never();
        }
        if (res.ok) {
            isConnected = true;
            updateConnectionUI();
            // Reload all data
            await loadAllData();
        }
    } catch (err) {
        console.error('Failed to connect bank:', err);
    }
}

async function disconnectBank() {
    try {
        const res = await postJson('/api/v1/plaid/disconnect', {});
        if (res.status === 401 || res.status === 403) {
            redirectToLogin();
            return await never();
        }
        if (res.ok) {
            isConnected = false;
            updateConnectionUI();
            // Reload with empty/mock data
            await loadAllData();
        }
    } catch (err) {
        console.error('Failed to disconnect bank:', err);
    }
}

// ----- Logout -----

async function logout() {
    try {
        await postJson('/api/v1/auth/logout', {});
    } catch {
        // Continue anyway
    }
    window.location.href = 'login.html';
}

// ----- Initialize -----

async function loadAllData() {
    await Promise.all([
        loadBudget(),
        loadSubscriptions(),
        loadDailySpending(),
        loadCategories(),
        loadGoals()
    ]);
}

async function init() {
    await requireAuth();
    await checkPlaidStatus();
    await loadAllData();
}

// Run on page load
init();
