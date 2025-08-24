// Global variables
let categoryChart = null;
let monthlyChart = null;
let comparisonChart1 = null;
let comparisonChart2 = null;
let transactions = [];
let currentFilters = { month: null, year: null };
let availableYears = [];
let availableMonths = [];
let comparisonMode = 'monthly'; // 'monthly' or 'yearly'

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Initialize the application
function initializeApp() {
    setupEventListeners();
    setDefaultDate();
    handleTypeChange(); // Initialize form state
    loadDashboard();
    loadTransactions();
}

// Setup all event listeners
function setupEventListeners() {
    // Tab navigation
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });

    // Transaction form
    document.getElementById('transaction-form').addEventListener('submit', handleTransactionSubmit);

    // Chat functionality
    document.getElementById('send-btn').addEventListener('click', sendChatMessage);
    document.getElementById('chat-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') sendChatMessage();
    });

    // Analysis buttons
    document.querySelectorAll('.analysis-btn').forEach(btn => {
        btn.addEventListener('click', () => getAnalysis(btn.dataset.analysis));
    });

    // Delete transaction
    document.getElementById('delete-btn').addEventListener('click', handleDeleteTransaction);

    // Filters
    document.getElementById('filter-category').addEventListener('change', filterTransactions);
    document.getElementById('filter-type').addEventListener('change', filterTransactions);

    // Dashboard filters
    document.getElementById('apply-filters').addEventListener('click', applyDashboardFilters);
    document.getElementById('reset-filters').addEventListener('click', resetDashboardFilters);
    document.getElementById('dashboard-year').addEventListener('change', updateMonthOptions);

    // Comparison chart updates
    document.getElementById('update-chart1').addEventListener('click', () => updateComparisonChart(1));
    document.getElementById('update-chart2').addEventListener('click', () => updateComparisonChart(2));
    
    // Comparison mode toggle
    document.getElementById('monthly-mode').addEventListener('click', () => switchComparisonMode('monthly'));
    document.getElementById('yearly-mode').addEventListener('click', () => switchComparisonMode('yearly'));
    
    // Transaction type change
    document.getElementById('type').addEventListener('change', handleTypeChange);
}

// Set default date to today
function setDefaultDate() {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('date').value = today;
}

// Handle transaction type change
function handleTypeChange() {
    const typeSelect = document.getElementById('type');
    const categoryGroup = document.getElementById('category-group');
    const categorySelect = document.getElementById('category');
    
    if (typeSelect.value === 'Income') {
        // Hide category for income
        categoryGroup.style.display = 'none';
        categorySelect.removeAttribute('required');
        categorySelect.value = 'Income'; // Set a default value for income
    } else {
        // Show category for expenses
        categoryGroup.style.display = 'flex';
        categorySelect.setAttribute('required', 'required');
        if (categorySelect.value === 'Income') {
            categorySelect.value = ''; // Reset if it was set to Income
        }
    }
}

// Switch between tabs
function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    document.getElementById(tabName).classList.add('active');

    // Load data for specific tabs
    if (tabName === 'dashboard') {
        loadDashboard();
    } else if (tabName === 'transactions') {
        loadTransactions();
    } else if (tabName === 'comparison') {
        loadComparisonTab();
    }
}

// Show loading overlay
function showLoading() {
    document.getElementById('loading-overlay').style.display = 'flex';
}

// Hide loading overlay
function hideLoading() {
    document.getElementById('loading-overlay').style.display = 'none';
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.classList.add('show');

    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}

// Handle transaction form submission
async function handleTransactionSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const type = formData.get('type');
    
    const transactionData = {
        date: formData.get('date'),
        amount: parseFloat(formData.get('amount')),
        category: type === 'Income' ? 'Income' : formData.get('category'),
        type: type,
        description: formData.get('description') || ''
    };

    try {
        showLoading();
        const response = await fetch('/api/transactions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(transactionData)
        });

        const result = await response.json();

        if (response.ok) {
            showNotification('Transaction added successfully!', 'success');
            e.target.reset();
            setDefaultDate();
            loadDashboard();
            loadTransactions();
        } else {
            showNotification(result.detail || 'Failed to add transaction', 'error');
        }
    } catch (error) {
        showNotification('Error adding transaction', 'error');
        console.error('Error:', error);
    } finally {
        hideLoading();
    }
}

// Load dashboard data
async function loadDashboard() {
    try {
        let url = '/api/dashboard';
        const params = new URLSearchParams();
        
        if (currentFilters.month) params.append('month', currentFilters.month);
        if (currentFilters.year) params.append('year', currentFilters.year);
        
        if (params.toString()) {
            url += '?' + params.toString();
        }

        const response = await fetch(url);
        const data = await response.json();

        if (response.ok) {
            updateMetrics(data.summary);
            updateCharts(data.category_chart, data.monthly_chart);
            updateRecentTransactions(data.recent_transactions);
            updateFilterOptions(data.available_years, data.available_months);
            
            // Store available years and months globally
            availableYears = data.available_years;
            availableMonths = data.available_months;
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// Update metrics cards
function updateMetrics(summary) {
    document.getElementById('total-income').textContent = `₹${summary.total_income.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
    document.getElementById('total-expenses').textContent = `₹${summary.total_expenses.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
    document.getElementById('net-balance').textContent = `₹${summary.net_balance.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
    document.getElementById('savings-rate').textContent = `${summary.savings_rate.toFixed(1)}%`;
}

// Update charts
function updateCharts(categoryData, monthlyData) {
    // Category Chart (Pie)
    const categoryCtx = document.getElementById('categoryChart').getContext('2d');
    
    if (categoryChart) {
        categoryChart.destroy();
    }

    if (categoryData.length > 0) {
        categoryChart = new Chart(categoryCtx, {
            type: 'pie',
            data: {
                labels: categoryData.map(item => item.category),
                datasets: [{
                    data: categoryData.map(item => item.amount),
                    backgroundColor: [
                        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                        '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF',
                        '#4BC0C0', '#FF6384', '#36A2EB', '#FFCE56'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    // Monthly Chart (Line)
    const monthlyCtx = document.getElementById('monthlyChart').getContext('2d');
    
    if (monthlyChart) {
        monthlyChart.destroy();
    }

    if (monthlyData.length > 0) {
        monthlyChart = new Chart(monthlyCtx, {
            type: 'line',
            data: {
                labels: monthlyData.map(item => item.month),
                datasets: [{
                    label: 'Monthly Expenses',
                    data: monthlyData.map(item => item.amount),
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '₹' + value.toLocaleString('en-IN');
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
}

// Update recent transactions
function updateRecentTransactions(recentTransactions) {
    const container = document.getElementById('recent-transactions-list');
    
    if (recentTransactions.length === 0) {
        container.innerHTML = '<p>No recent transactions found.</p>';
        return;
    }

    container.innerHTML = recentTransactions.map(transaction => `
        <div class="transaction-item">
            <div class="transaction-info">
                <span class="transaction-category">${transaction.category.split(' ')[0]}</span>
                <div class="transaction-details">
                    <h4>${transaction.category}</h4>
                    <p>${transaction.date}</p>
                </div>
            </div>
            <div class="transaction-amount ${transaction.type.toLowerCase()}">
                ${transaction.type === 'Income' ? '+' : '-'}₹${transaction.amount.toFixed(2)}
            </div>
        </div>
    `).join('');
}

// Load all transactions
async function loadTransactions() {
    try {
        const response = await fetch('/api/transactions');
        transactions = await response.json();

        if (response.ok) {
            updateTransactionsList(transactions);
            updateFilters();
            updateDeleteOptions();
        }
    } catch (error) {
        console.error('Error loading transactions:', error);
    }
}

// Update transactions list
function updateTransactionsList(transactionsToShow) {
    const container = document.getElementById('transactions-list');
    
    if (transactionsToShow.length === 0) {
        container.innerHTML = '<div class="transaction-item"><p>No transactions found.</p></div>';
        return;
    }

    container.innerHTML = transactionsToShow.map(transaction => `
        <div class="transaction-item">
            <div class="transaction-info">
                <span class="transaction-category">${transaction.category.split(' ')[0]}</span>
                <div class="transaction-details">
                    <h4>${transaction.category}</h4>
                    <p>${transaction.date} ${transaction.description ? '• ' + transaction.description : ''}</p>
                </div>
            </div>
            <div class="transaction-amount ${transaction.type.toLowerCase()}">
                ${transaction.type === 'Income' ? '+' : '-'}₹${transaction.amount.toFixed(2)}
            </div>
        </div>
    `).join('');
}

// Update filter options
function updateFilters() {
    const categoryFilter = document.getElementById('filter-category');
    const categories = [...new Set(transactions.map(t => t.category))];
    
    categoryFilter.innerHTML = '<option value="">All Categories</option>' +
        categories.map(cat => `<option value="${cat}">${cat}</option>`).join('');
}

// Filter transactions
function filterTransactions() {
    const categoryFilter = document.getElementById('filter-category').value;
    const typeFilter = document.getElementById('filter-type').value;

    let filtered = transactions;

    if (categoryFilter) {
        filtered = filtered.filter(t => t.category === categoryFilter);
    }

    if (typeFilter) {
        filtered = filtered.filter(t => t.type === typeFilter);
    }

    updateTransactionsList(filtered);
}

// Update delete options
function updateDeleteOptions() {
    const deleteSelect = document.getElementById('delete-transaction-select');
    
    deleteSelect.innerHTML = '<option value="">Choose a transaction to delete...</option>' +
        transactions.map(t => 
            `<option value="${t.id}">ID: ${t.id} | ${t.date} | ${t.category} | ₹${t.amount.toFixed(2)} | ${t.type}</option>`
        ).join('');
}

// Handle delete transaction
async function handleDeleteTransaction() {
    const selectElement = document.getElementById('delete-transaction-select');
    const transactionId = selectElement.value;

    if (!transactionId) {
        showNotification('Please select a transaction to delete', 'error');
        return;
    }

    if (!confirm('Are you sure you want to delete this transaction?')) {
        return;
    }

    try {
        showLoading();
        const response = await fetch(`/api/transactions/${transactionId}`, {
            method: 'DELETE'
        });

        const result = await response.json();

        if (response.ok) {
            showNotification('Transaction deleted successfully!', 'success');
            loadDashboard();
            loadTransactions();
        } else {
            showNotification(result.detail || 'Failed to delete transaction', 'error');
        }
    } catch (error) {
        showNotification('Error deleting transaction', 'error');
        console.error('Error:', error);
    } finally {
        hideLoading();
    }
}

// Send chat message
async function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();

    if (!message) return;

    // Add user message to chat
    addChatMessage(message, 'user');
    input.value = '';

    try {
        showLoading();
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message })
        });

        const result = await response.json();

        if (response.ok) {
            addChatMessage(result.response, 'assistant');
        } else {
            addChatMessage('Sorry, I encountered an error. Please try again.', 'assistant');
        }
    } catch (error) {
        addChatMessage('Sorry, I encountered an error. Please try again.', 'assistant');
        console.error('Error:', error);
    } finally {
        hideLoading();
    }
}

// Add message to chat
function addChatMessage(message, sender) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    messageDiv.innerHTML = `
        <div class="message-content">${message}</div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Get analysis
async function getAnalysis(type) {
    const endpoints = {
        'spending': '/api/analysis/spending',
        'budget': '/api/analysis/budget',
        'savings': '/api/analysis/savings'
    };

    try {
        showLoading();
        const response = await fetch(endpoints[type]);
        const result = await response.json();

        if (response.ok) {
            const resultDiv = document.getElementById('analysis-result');
            const key = type === 'spending' ? 'analysis' : type === 'budget' ? 'suggestions' : 'tips';
            resultDiv.textContent = result[key];
            resultDiv.style.display = 'block';
        }
    } catch (error) {
        console.error('Error getting analysis:', error);
        showNotification('Error getting analysis', 'error');
    } finally {
        hideLoading();
    }
}

// Dashboard filter functions
function updateFilterOptions(availableYears, availableMonths) {
    const yearSelect = document.getElementById('dashboard-year');
    const monthSelect = document.getElementById('dashboard-month');
    
    // Update year options
    yearSelect.innerHTML = '<option value="">All Years</option>';
    availableYears.forEach(year => {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year;
        if (year === currentFilters.year) option.selected = true;
        yearSelect.appendChild(option);
    });
    
    // Set default to current year if no filter applied
    if (!currentFilters.year && !currentFilters.month) {
        const currentYear = new Date().getFullYear();
        const currentMonth = new Date().getMonth() + 1;
        
        if (availableYears.includes(currentYear)) {
            yearSelect.value = currentYear;
            currentFilters.year = currentYear;
        }
        
        if (availableMonths.includes(currentMonth)) {
            monthSelect.value = currentMonth;
            currentFilters.month = currentMonth;
        }
    }
}

function updateMonthOptions() {
    // This function can be enhanced to show only available months for selected year
    // For now, it keeps all months available
}

function applyDashboardFilters() {
    const year = document.getElementById('dashboard-year').value;
    const month = document.getElementById('dashboard-month').value;
    
    currentFilters.year = year ? parseInt(year) : null;
    currentFilters.month = month ? parseInt(month) : null;
    
    loadDashboard();
}

function resetDashboardFilters() {
    currentFilters = { month: null, year: null };
    document.getElementById('dashboard-year').value = '';
    document.getElementById('dashboard-month').value = '';
    loadDashboard();
}

// Comparison tab functions
async function loadComparisonTab() {
    // Populate year dropdowns for comparison charts
    populateComparisonFilters();
    
    // Set default values (current month for chart 1, previous month for chart 2)
    const currentDate = new Date();
    const currentYear = currentDate.getFullYear();
    const currentMonth = currentDate.getMonth() + 1;
    const previousMonth = currentMonth === 1 ? 12 : currentMonth - 1;
    const previousYear = currentMonth === 1 ? currentYear - 1 : currentYear;
    
    // Set defaults if data is available
    if (availableYears.includes(currentYear)) {
        document.getElementById('chart1-year').value = currentYear;
        document.getElementById('chart1-month').value = currentMonth;
    }
    
    if (availableYears.includes(previousYear)) {
        document.getElementById('chart2-year').value = previousYear;
        document.getElementById('chart2-month').value = previousMonth;
    }
    
    // Load initial charts
    updateComparisonChart(1);
    updateComparisonChart(2);
}

function populateComparisonFilters() {
    const chart1Year = document.getElementById('chart1-year');
    const chart2Year = document.getElementById('chart2-year');
    
    // Clear existing options
    chart1Year.innerHTML = '<option value="">Select Year</option>';
    chart2Year.innerHTML = '<option value="">Select Year</option>';
    
    // Add available years
    availableYears.forEach(year => {
        const option1 = document.createElement('option');
        option1.value = year;
        option1.textContent = year;
        chart1Year.appendChild(option1);
        
        const option2 = document.createElement('option');
        option2.value = year;
        option2.textContent = year;
        chart2Year.appendChild(option2);
    });
}

async function updateComparisonChart(chartNumber) {
    const year = document.getElementById(`chart${chartNumber}-year`).value;
    const month = document.getElementById(`chart${chartNumber}-month`).value;
    
    // Check required fields based on mode
    if (!year || (comparisonMode === 'monthly' && !month)) {
        // Clear chart if no selection
        if (chartNumber === 1 && comparisonChart1) {
            comparisonChart1.destroy();
            comparisonChart1 = null;
        } else if (chartNumber === 2 && comparisonChart2) {
            comparisonChart2.destroy();
            comparisonChart2 = null;
        }
        const requiredFields = comparisonMode === 'monthly' ? 'year and month' : 'year';
        document.getElementById(`chart${chartNumber}-summary`).innerHTML = `<p>Please select ${requiredFields}.</p>`;
        updateComparisonInsights();
        return;
    }
    
    try {
        showLoading();
        let response;
        
        if (comparisonMode === 'monthly') {
            response = await fetch(`/api/dashboard?year=${year}&month=${month}`);
        } else {
            response = await fetch(`/api/dashboard/yearly?year=${year}`);
        }
        
        const data = await response.json();
        
        if (response.ok) {
            createComparisonPieChart(chartNumber, data.category_chart, data.summary, year, month);
            updateComparisonInsights();
        }
    } catch (error) {
        console.error(`Error loading chart ${chartNumber} data:`, error);
        showNotification(`Error loading chart ${chartNumber} data`, 'error');
    } finally {
        hideLoading();
    }
}

function createComparisonPieChart(chartNumber, categoryData, summary, year, month) {
    const ctx = document.getElementById(`comparisonChart${chartNumber}`).getContext('2d');
    
    // Destroy existing chart
    if (chartNumber === 1 && comparisonChart1) {
        comparisonChart1.destroy();
    } else if (chartNumber === 2 && comparisonChart2) {
        comparisonChart2.destroy();
    }
    
    // Create chart title based on mode
    let chartTitle;
    if (comparisonMode === 'monthly') {
        const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        chartTitle = `${monthNames[month - 1]} ${year}`;
    } else {
        chartTitle = `Year ${year}`;
    }
    
    if (categoryData.length > 0) {
        const chart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: categoryData.map(item => item.category),
                datasets: [{
                    data: categoryData.map(item => item.amount),
                    backgroundColor: [
                        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                        '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF',
                        '#4BC0C0', '#FF6384', '#36A2EB', '#FFCE56'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: chartTitle,
                        font: {
                            size: 16,
                            weight: 'bold'
                        }
                    },
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
        
        if (chartNumber === 1) {
            comparisonChart1 = chart;
        } else {
            comparisonChart2 = chart;
        }
    }
    
    // Update summary
    const summaryDiv = document.getElementById(`chart${chartNumber}-summary`);
    summaryDiv.innerHTML = `
        <div class="summary-stats">
            <div class="stat-item">
                <span class="stat-label">Total Expenses:</span>
                <span class="stat-value expense">₹${summary.total_expenses.toLocaleString('en-IN', {minimumFractionDigits: 2})}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Total Income:</span>
                <span class="stat-value income">₹${summary.total_income.toLocaleString('en-IN', {minimumFractionDigits: 2})}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Net Balance:</span>
                <span class="stat-value ${summary.net_balance >= 0 ? 'income' : 'expense'}">₹${summary.net_balance.toLocaleString('en-IN', {minimumFractionDigits: 2})}</span>
            </div>
        </div>
    `;
}

function switchComparisonMode(mode) {
    comparisonMode = mode;
    
    // Update toggle buttons
    document.querySelectorAll('.toggle-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById(`${mode}-mode`).classList.add('active');
    
    // Show/hide month selectors based on mode
    const monthSelectors = document.querySelectorAll('.monthly-only');
    monthSelectors.forEach(selector => {
        if (mode === 'yearly') {
            selector.style.display = 'none';
        } else {
            selector.style.display = 'flex';
        }
    });
    
    // Clear existing charts and summaries
    if (comparisonChart1) {
        comparisonChart1.destroy();
        comparisonChart1 = null;
    }
    if (comparisonChart2) {
        comparisonChart2.destroy();
        comparisonChart2 = null;
    }
    
    // Clear month selections if switching to yearly mode
    if (mode === 'yearly') {
        document.getElementById('chart1-month').value = '';
        document.getElementById('chart2-month').value = '';
    }
    
    // Clear summaries
    document.getElementById('chart1-summary').innerHTML = `<p>Please select ${mode === 'monthly' ? 'year and month' : 'year'}.</p>`;
    document.getElementById('chart2-summary').innerHTML = `<p>Please select ${mode === 'monthly' ? 'year and month' : 'year'}.</p>`;
    
    // Update insights
    updateComparisonInsights();
}

function updateComparisonInsights() {
    const chart1Year = document.getElementById('chart1-year').value;
    const chart1Month = document.getElementById('chart1-month').value;
    const chart2Year = document.getElementById('chart2-year').value;
    const chart2Month = document.getElementById('chart2-month').value;
    
    const insightsDiv = document.getElementById('comparison-insights');
    
    // Check required fields based on mode
    const requiredFieldsPresent = comparisonMode === 'monthly' 
        ? (chart1Year && chart1Month && chart2Year && chart2Month)
        : (chart1Year && chart2Year);
    
    if (!requiredFieldsPresent) {
        const requiredFields = comparisonMode === 'monthly' ? 'periods for both charts' : 'years for both charts';
        insightsDiv.innerHTML = `<p>Select ${requiredFields} to see comparison insights.</p>`;
        return;
    }
    
    // Get data from chart summaries
    const chart1Summary = document.getElementById('chart1-summary');
    const chart2Summary = document.getElementById('chart2-summary');
    
    if (!chart1Summary.querySelector('.summary-stats') || !chart2Summary.querySelector('.summary-stats')) {
        insightsDiv.innerHTML = '<p>Loading comparison insights...</p>';
        return;
    }
    
    // Extract expense values
    const chart1ExpenseText = chart1Summary.querySelector('.stat-value.expense').textContent;
    const chart2ExpenseText = chart2Summary.querySelector('.stat-value.expense').textContent;
    
    const chart1Expense = parseFloat(chart1ExpenseText.replace(/[₹,]/g, ''));
    const chart2Expense = parseFloat(chart2ExpenseText.replace(/[₹,]/g, ''));
    
    const difference = chart1Expense - chart2Expense;
    const percentChange = chart2Expense > 0 ? ((difference / chart2Expense) * 100) : 0;
    
    // Create period labels based on mode
    let period1Label, period2Label;
    if (comparisonMode === 'monthly') {
        const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
        period1Label = `${monthNames[chart1Month - 1]} ${chart1Year}`;
        period2Label = `${monthNames[chart2Month - 1]} ${chart2Year}`;
    } else {
        period1Label = `Year ${chart1Year}`;
        period2Label = `Year ${chart2Year}`;
    }
    
    let insightText = `
        <div class="insight-item">
            <h4>${comparisonMode === 'monthly' ? 'Monthly' : 'Yearly'} Spending Comparison</h4>
            <p><strong>${period1Label}</strong> vs <strong>${period2Label}</strong></p>
        </div>
        <div class="insight-item">
            <h4>Difference</h4>
            <p class="${difference >= 0 ? 'expense' : 'income'}">
                ${difference >= 0 ? '+' : ''}₹${Math.abs(difference).toLocaleString('en-IN', {minimumFractionDigits: 2})}
                (${percentChange >= 0 ? '+' : ''}${percentChange.toFixed(1)}%)
            </p>
        </div>
        <div class="insight-item">
            <h4>Analysis</h4>
            <p>
                ${difference > 0 
                    ? `You spent ₹${Math.abs(difference).toLocaleString('en-IN')} more in ${period1Label} compared to ${period2Label}.`
                    : difference < 0 
                    ? `You spent ₹${Math.abs(difference).toLocaleString('en-IN')} less in ${period1Label} compared to ${period2Label}. Great job on reducing expenses!`
                    : `Your spending was exactly the same in both periods.`
                }
            </p>
        </div>
    `;
    
    insightsDiv.innerHTML = insightText;
}