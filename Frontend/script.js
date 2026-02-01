// ----- API Utility -----

async function fetchWithFallback(url, fallbackData, options = {}) {
    try {
        const res = await fetch(url, {
            credentials: 'include',
            ...options
        });
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

// ----- Budget -----

function updateBudgetUI() {
    const percentage = Math.min((spent / limit) * 100, 100).toFixed(0);
    
    const budgetLimitEl = document.getElementById('budget-limit');
    const progressTextEl = document.getElementById('progress-text');
    const spentAmountEl = document.getElementById('spent-amount');
    const progressBarEl = document.getElementById('progress-bar');
    
    if (budgetLimitEl) budgetLimitEl.innerText = limit;
    if (progressTextEl) progressTextEl.innerText = `${percentage}%`;
    if (spentAmountEl) spentAmountEl.innerText = spent.toFixed(2);
    if (progressBarEl) {
        progressBarEl.style.width = `${percentage}%`;
        progressBarEl.style.backgroundColor = percentage >= 100 ? "#ff4d4d" : "#4CAF50";
    }
}

async function loadBudget() {
    const data = await fetchWithFallback('/api/v1/budget', MOCK_BUDGET);
    spent = data.spent || 0;
    limit = data.limit || 3000;
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
                limit = data.limit;
                spent = data.spent;
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
        const row = createSubscriptionRow(sub.name, sub.icon, `$${sub.amount}`, sub.date);
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
    subscriptionData = await fetchWithFallback('/api/v1/subscriptions', MOCK_SUBSCRIPTIONS);
    renderSubscriptionsUI();
}

// ----- Daily Spending -----

function renderSpendingUI() {
    const container = document.getElementById('transaction-history');
    if (!container) return;
    
    let total = 0;
    container.innerHTML = '';
    
    dailyTransactions.forEach(item => {
        total += item.amount;
        
        const row = document.createElement('div');
        row.className = 'spending-row';
        
        const nameSpan = document.createElement('span');
        nameSpan.className = 'spending-name';
        nameSpan.textContent = item.name;
        
        const iconSpan = document.createElement('span');
        iconSpan.className = 'spending-icon';
        iconSpan.textContent = item.icon;
        
        const amountSpan = document.createElement('span');
        amountSpan.className = 'spending-amount';
        amountSpan.textContent = `$${item.amount.toFixed(2)}`;
        
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
    dailyTransactions = await fetchWithFallback('/api/v1/spending/daily', MOCK_TRANSACTIONS);
    renderSpendingUI();
}

// ----- Spending Chart -----

function updateChartUI() {
    const chart = document.getElementById('spending-chart');
    const legend = document.getElementById('chart-legend');
    const totalDisplay = document.getElementById('total-spent-display');
    
    if (!chart || !legend || !totalDisplay) return;
    
    const total = spendingCategories.reduce((sum, cat) => sum + cat.amount, 0);
    totalDisplay.innerText = `$${total}`;
    
    if (total === 0) {
        chart.style.background = `conic-gradient(#eee 0% 100%)`;
        legend.innerHTML = '';
        return;
    }
    
    let gradientString = "";
    let cumulativePercent = 0;
    
    legend.innerHTML = "";
    
    spendingCategories.forEach((cat, index) => {
        const percent = (cat.amount / total) * 100;
        const start = cumulativePercent;
        cumulativePercent += percent;
        
        gradientString += `${cat.color} ${start}% ${cumulativePercent}%`;
        if (index < spendingCategories.length - 1) gradientString += ", ";
        
        const item = document.createElement('div');
        item.className = 'legend-item';
        
        const dot = document.createElement('span');
        dot.className = 'dot';
        dot.style.background = cat.color;
        
        const label = document.createElement('span');
        label.textContent = `${cat.name}: $${cat.amount}`;
        
        item.appendChild(dot);
        item.appendChild(label);
        legend.appendChild(item);
    });
    
    chart.style.background = `conic-gradient(${gradientString})`;
}

async function loadCategories() {
    spendingCategories = await fetchWithFallback('/api/v1/spending/categories', MOCK_CATEGORIES);
    updateChartUI();
}

// ----- Goals -----

function renderGoalsUI() {
    const list = document.getElementById('goals-list');
    if (!list) return;
    
    list.innerHTML = '';
    
    goals.forEach(goal => {
        const div = document.createElement('div');
        div.className = 'goal-item';
        
        const nameSpan = document.createElement('span');
        nameSpan.textContent = goal.name;
        
        const monthlySpan = document.createElement('span');
        monthlySpan.textContent = `$${goal.monthly}/m`;
        
        div.appendChild(nameSpan);
        div.appendChild(monthlySpan);
        list.appendChild(div);
    });
}

async function loadGoals() {
    goals = await fetchWithFallback('/api/v1/goals', MOCK_GOALS);
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
    window.location.href = '/login.html';
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
    await checkPlaidStatus();
    await loadAllData();
}

// Run on page load
init();
