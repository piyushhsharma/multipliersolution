// Data Analytics Dashboard JavaScript

// Global variables
let revenueChart = null;
let categoryChart = null;
let originalRevenueData = [];
let originalCustomersData = [];
let originalRegionsData = [];
let currentCustomersSort = { column: null, ascending: true };
let currentRegionsSort = { column: null, ascending: true };

// API base URL
const API_BASE_URL = 'http://localhost:8000/api';

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
});

// Main initialization function
async function initializeDashboard() {
    showLoading(true);
    try {
        await loadSummaryData();
        await loadRevenueData();
        await loadCustomersData();
        await loadCategoryData();
        await loadRegionsData();
        showLoading(false);
    } catch (error) {
        showError('Failed to load dashboard data: ' + error.message);
        showLoading(false);
    }
}

// Loading indicator functions
function showLoading(show) {
    const loadingIndicator = document.getElementById('loadingIndicator');
    loadingIndicator.style.display = show ? 'flex' : 'none';
}

// Error handling functions
function showError(message) {
    const errorElement = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');
    errorText.textContent = message;
    errorElement.style.display = 'flex';
}

function hideError() {
    const errorElement = document.getElementById('errorMessage');
    errorElement.style.display = 'none';
}

// API request helper
async function fetchAPI(endpoint) {
    try {
        const response = await fetch(`${API_BASE_URL}/${endpoint}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`Error fetching ${endpoint}:`, error);
        throw error;
    }
}

// Load summary data
async function loadSummaryData() {
    try {
        const summary = await fetchAPI('summary');
        
        document.getElementById('totalCustomers').textContent = summary.total_customers.toLocaleString();
        document.getElementById('totalOrders').textContent = summary.total_orders.toLocaleString();
        document.getElementById('totalRevenue').textContent = '$' + summary.total_revenue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        document.getElementById('avgOrderValue').textContent = '$' + summary.avg_order_value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        
    } catch (error) {
        console.error('Error loading summary data:', error);
        throw error;
    }
}

// Load revenue data and create chart
async function loadRevenueData() {
    try {
        const data = await fetchAPI('revenue');
        originalRevenueData = data;
        createRevenueChart(data);
    } catch (error) {
        console.error('Error loading revenue data:', error);
        throw error;
    }
}

// Create revenue trend chart
function createRevenueChart(data) {
    const ctx = document.getElementById('revenueChart').getContext('2d');
    
    if (revenueChart) {
        revenueChart.destroy();
    }
    
    revenueChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(item => item.month),
            datasets: [{
                label: 'Monthly Revenue',
                data: data.map(item => item.total_revenue),
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 5,
                pointHoverRadius: 8,
                pointBackgroundColor: '#667eea',
                pointBorderColor: '#fff',
                pointBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        font: {
                            size: 14,
                            weight: '600'
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return 'Revenue: $' + context.parsed.y.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// Filter revenue chart by date
function filterRevenueChart() {
    const filterValue = document.getElementById('dateFilter').value.trim();
    
    if (!filterValue) {
        resetRevenueChart();
        return;
    }
    
    const filteredData = originalRevenueData.filter(item => 
        item.month.includes(filterValue)
    );
    
    if (filteredData.length === 0) {
        showError('No data found for the specified filter');
        return;
    }
    
    createRevenueChart(filteredData);
}

// Reset revenue chart
function resetRevenueChart() {
    document.getElementById('dateFilter').value = '';
    createRevenueChart(originalRevenueData);
}

// Load customers data
async function loadCustomersData() {
    try {
        const data = await fetchAPI('top-customers');
        originalCustomersData = data;
        populateCustomersTable(data);
    } catch (error) {
        console.error('Error loading customers data:', error);
        throw error;
    }
}

// Populate customers table
function populateCustomersTable(data) {
    const tbody = document.getElementById('customersTableBody');
    
    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="loading-row">No customer data available</td></tr>';
        return;
    }
    
    tbody.innerHTML = data.map(customer => `
        <tr>
            <td class="font-weight-bold">${customer.name || 'N/A'}</td>
            <td>${customer.region || 'N/A'}</td>
            <td class="text-right color-primary">$${(customer.total_spend || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
            <td class="text-right">${customer.order_count || 0}</td>
            <td class="text-center">
                <span class="status-badge ${customer.churned ? 'status-churned' : 'status-active'}">
                    ${customer.churned ? 'Churned' : 'Active'}
                </span>
            </td>
        </tr>
    `).join('');
}

// Search customers
function searchCustomers() {
    const searchTerm = document.getElementById('customerSearch').value.trim().toLowerCase();
    
    if (!searchTerm) {
        populateCustomersTable(originalCustomersData);
        return;
    }
    
    const filteredData = originalCustomersData.filter(customer => 
        (customer.name && customer.name.toLowerCase().includes(searchTerm)) ||
        (customer.region && customer.region.toLowerCase().includes(searchTerm))
    );
    
    populateCustomersTable(filteredData);
}

// Reset customer search
function resetCustomerSearch() {
    document.getElementById('customerSearch').value = '';
    populateCustomersTable(originalCustomersData);
}

// Sort customers table
function sortTable(column) {
    if (currentCustomersSort.column === column) {
        currentCustomersSort.ascending = !currentCustomersSort.ascending;
    } else {
        currentCustomersSort.column = column;
        currentCustomersSort.ascending = true;
    }
    
    const sortedData = [...originalCustomersData].sort((a, b) => {
        let aVal = a[column];
        let bVal = b[column];
        
        // Handle different data types
        if (column === 'total_spend' || column === 'order_count') {
            aVal = parseFloat(aVal) || 0;
            bVal = parseFloat(bVal) || 0;
        } else if (column === 'churned') {
            aVal = aVal ? 1 : 0;
            bVal = bVal ? 1 : 0;
        } else {
            aVal = (aVal || '').toString().toLowerCase();
            bVal = (bVal || '').toString().toLowerCase();
        }
        
        if (aVal < bVal) return currentCustomersSort.ascending ? -1 : 1;
        if (aVal > bVal) return currentCustomersSort.ascending ? 1 : -1;
        return 0;
    });
    
    populateCustomersTable(sortedData);
}

// Load category data and create chart
async function loadCategoryData() {
    try {
        const data = await fetchAPI('categories');
        createCategoryChart(data);
    } catch (error) {
        console.error('Error loading category data:', error);
        throw error;
    }
}

// Create category performance chart
function createCategoryChart(data) {
    const ctx = document.getElementById('categoryChart').getContext('2d');
    
    if (categoryChart) {
        categoryChart.destroy();
    }
    
    categoryChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(item => item.category),
            datasets: [{
                label: 'Total Revenue',
                data: data.map(item => item.total_revenue),
                backgroundColor: '#667eea',
                borderColor: '#5a6fd8',
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        font: {
                            size: 14,
                            weight: '600'
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return 'Revenue: $' + context.parsed.y.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
                        },
                        afterLabel: function(context) {
                            const item = data[context.dataIndex];
                            return [
                                'Orders: ' + item.order_count,
                                'Avg Order: $' + item.avg_order_value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
                            ];
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// Load regions data
async function loadRegionsData() {
    try {
        const data = await fetchAPI('regions');
        originalRegionsData = data;
        populateRegionsTable(data);
    } catch (error) {
        console.error('Error loading regions data:', error);
        throw error;
    }
}

// Populate regions table
function populateRegionsTable(data) {
    const tbody = document.getElementById('regionsTableBody');
    
    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="loading-row">No regional data available</td></tr>';
        return;
    }
    
    tbody.innerHTML = data.map(region => `
        <tr>
            <td class="font-weight-bold">${region.region || 'N/A'}</td>
            <td class="text-right">${region.customer_count || 0}</td>
            <td class="text-right">${region.order_count || 0}</td>
            <td class="text-right color-primary">$${(region.total_revenue || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
            <td class="text-right">$${(region.avg_revenue_per_customer || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
        </tr>
    `).join('');
}

// Sort regions table
function sortRegionsTable(column) {
    if (currentRegionsSort.column === column) {
        currentRegionsSort.ascending = !currentRegionsSort.ascending;
    } else {
        currentRegionsSort.column = column;
        currentRegionsSort.ascending = true;
    }
    
    const sortedData = [...originalRegionsData].sort((a, b) => {
        let aVal = a[column];
        let bVal = b[column];
        
        // Handle numeric columns
        if (['customer_count', 'order_count', 'total_revenue', 'avg_revenue_per_customer'].includes(column)) {
            aVal = parseFloat(aVal) || 0;
            bVal = parseFloat(bVal) || 0;
        } else {
            aVal = (aVal || '').toString().toLowerCase();
            bVal = (bVal || '').toString().toLowerCase();
        }
        
        if (aVal < bVal) return currentRegionsSort.ascending ? -1 : 1;
        if (aVal > bVal) return currentRegionsSort.ascending ? 1 : -1;
        return 0;
    });
    
    populateRegionsTable(sortedData);
}

// Utility function to format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(amount);
}

// Utility function to debounce search
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Add debounced search for customers
document.getElementById('customerSearch').addEventListener('input', debounce(searchCustomers, 300));

// Add enter key support for search inputs
document.getElementById('customerSearch').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        searchCustomers();
    }
});

document.getElementById('dateFilter').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        filterRevenueChart();
    }
});

// Handle window resize for responsive charts
window.addEventListener('resize', debounce(() => {
    if (revenueChart) revenueChart.resize();
    if (categoryChart) categoryChart.resize();
}, 250));
