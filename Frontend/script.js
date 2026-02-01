let spent = 0;
let limit = 3000;

function updateUI() {
  const percentage = Math.min((spent / limit) * 100, 100).toFixed(0);
  
  document.getElementById('budget-limit').innerText = limit;
  document.getElementById('progress-text').innerText = `${percentage}%`;
  

  document.getElementById('progress-bar').style.width = `${percentage}%`;
  

  const bar = document.getElementById('progress-bar');
  bar.style.backgroundColor = percentage >= 100 ? "#ff4d4d" : "#4CAF50";
}


function updateBudget() {
  const newLimit = document.getElementById('new-limit').value;
  if (newLimit >= 0) {
    limit = newLimit;
    updateUI();
    toggleEdit();
  }
}

function toggleEdit() {
  const div = document.getElementById('edit-fields');
  div.style.display = div.style.display === 'none' ? 'block' : 'none';
}

// Initialize
updateUI();

// Mock JSON data
const subscriptionData = [
  {
    name: "Crunchyroll",
    icon: "📺",
    amount: 7.99,
    date: "Feb 15"
  }
];

function renderSubscriptions() {
  const container = document.getElementById('subscription-list');
  container.innerHTML = ''; // Clear current list

  // 1. Render the active "Filler" subscription
  subscriptionData.forEach(sub => {
    const row = createRowHTML(sub.name, sub.icon, `$${sub.amount}`, sub.date);
    container.appendChild(row);
  });

  // 2. Render 3 Blank Placeholder Rows
  for (let i = 0; i < 3; i++) {
    const emptyRow = createRowHTML('', '', '', '');
    emptyRow.classList.add('empty');
    container.appendChild(emptyRow);
  }
}

function createRowHTML(name, icon, amount, date) {
  const div = document.createElement('div');
  div.className = 'sub-row';
  div.innerHTML = `
    <span class="sub-name">${name}</span>
    <span class="sub-icon">${icon}</span>
    <span class="sub-amount">${amount}</span>
    <span class="sub-date">${date}</span>
  `;
  return div;
}

// Initial Load
renderSubscriptions();
const dailyTransactions = [
  { name: "Kroger", icon: "🛒", amount: 45.20 },
  { name: "Taco Bell", icon: "🌮", amount: 12.85 },
  { name: "Chic-fil-a", icon: "🍔", amount: 15.40 },
  { name: "Starbucks", icon: "☕", amount: 6.50 },
  { name: "Gas Station", icon: "⛽", amount: 40.00 }
];

function renderSpending() {
  const container = document.getElementById('transaction-history');
  let total = 0;
  
  container.innerHTML = '';

  dailyTransactions.forEach(item => {
    total += item.amount;
    
    const row = document.createElement('div');
    row.className = 'spending-row';
    row.innerHTML = `
      <span class="spending-name">${item.name}</span>
      <span class="spending-icon">${item.icon}</span>
      <span class="spending-amount">$${item.amount.toFixed(2)}</span>
    `;
    container.appendChild(row);
  });

  // Update the Total Row
  document.getElementById('daily-total').innerText = `$${total.toFixed(2)}`;
}

// Initial Load
renderSpending();

// Mock Data (CRUD-ready)
const spendingCategories = [
  { name: "Rent", amount: 1200, color: "#4CAF50" }, // Green
  { name: "Food", amount: 400, color: "#FF9800" },  // Orange
  { name: "Bills", amount: 250, color: "#2196F3" }, // Blue
  { name: "Fun", amount: 150, color: "#E91E63" }    // Pink
];

function updateChart() {
  const chart = document.getElementById('spending-chart');
  const legend = document.getElementById('chart-legend');
  const totalDisplay = document.getElementById('total-spent-display');
  
  const total = spendingCategories.reduce((sum, cat) => sum + cat.amount, 0);
  totalDisplay.innerText = `$${total}`;

  if (total === 0) {
    chart.style.background = `conic-gradient(#eee 0% 100%)`;
    return;
  }

  let gradientString = "";
  let cumulativePercent = 0;

  legend.innerHTML = ""; // Clear legend

  spendingCategories.forEach((cat, index) => {
    const percent = (cat.amount / total) * 100;
    const start = cumulativePercent;
    cumulativePercent += percent;
    
    // Build the CSS Conic Gradient string
    gradientString += `${cat.color} ${start}% ${cumulativePercent}%`;
    if (index < spendingCategories.length - 1) gradientString += ", ";

    // Add to Legend
    const item = document.createElement('div');
    item.className = 'legend-item';
    item.innerHTML = `
      <span class="dot" style="background:${cat.color}"></span>
      <span>${cat.name}: $${cat.amount}</span>
    `;
    legend.appendChild(item);
  });

  chart.style.background = `conic-gradient(${gradientString})`;
}

// Initial Run
updateChart();

let goals = [
  { name: "Japan 2030", date: "Jan 2030", monthly: 100, total: 12000 }
];

function openModal() {
  document.getElementById('goal-modal').style.display = 'flex';
}

function closeModal() {
  document.getElementById('goal-modal').style.display = 'none';
}

function saveGoal() {
  const name = document.getElementById('goal-name').value;
  const dateValue = document.getElementById('goal-date').value; // YYYY-MM
  const monthly = document.getElementById('goal-monthly').value;
  const total = document.getElementById('goal-total').value;

  if (name && dateValue && monthly && total) {
    // Format the date for the display
    const [year, month] = dateValue.split('-');
    const formattedDate = `${month}/${year}`;

    // Add to local data (Create)
    goals.push({ name, date: formattedDate, monthly, total });
    
    renderGoals();
    closeModal();
    
    // Clear inputs
    document.getElementById('goal-name').value = '';
    document.getElementById('goal-monthly').value = '';
  }
}

function renderGoals() {
  const list = document.getElementById('goals-list');
  list.innerHTML = '';

  goals.forEach(goal => {
    const div = document.createElement('div');
    div.className = 'goal-item';
    div.innerHTML = `
      <span>${goal.name}</span>
      <span>$${goal.monthly}/m</span>
    `;
    list.appendChild(div);
  });
}

// Initial Render
renderGoals();