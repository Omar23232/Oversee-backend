document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const alertsContainer = document.querySelector('.alerts-container');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const emptyState = document.getElementById('emptyState');
    const tableBody = document.getElementById('alertsTableBody');
    const filterToggle = document.getElementById('toggleFilters');
    const filterOptions = document.getElementById('filterOptions');
    const severityFilter = document.getElementById('severityFilter');
    const dateFilter = document.getElementById('dateFilter');

    // State
    let alerts = [];
    let filters = {
        severity: '',
        timeRange: '24h'
    };

    // Initialize filters
    if (filterToggle) {
        filterToggle.addEventListener('click', () => {
            const isExpanded = filterToggle.getAttribute('aria-expanded') === 'true';
            filterToggle.setAttribute('aria-expanded', !isExpanded);
            filterOptions.hidden = isExpanded;
            filterToggle.innerHTML = `<i class="fas fa-filter"></i> ${isExpanded ? 'Show' : 'Hide'} Filters`;
        });
    }

    if (severityFilter) {
        severityFilter.addEventListener('change', () => {
            filters.severity = severityFilter.value;
            applyFilters();
        });
    }

    if (dateFilter) {
        dateFilter.addEventListener('change', () => {
            filters.timeRange = dateFilter.value;
            applyFilters();
        });
    }


const showAcknowledgedCheckbox = document.getElementById('showAcknowledgedCheckbox');
let showAcknowledged = false;

if (showAcknowledgedCheckbox) {
    showAcknowledgedCheckbox.addEventListener('change', () => {
        showAcknowledged = showAcknowledgedCheckbox.checked;
        fetchAlerts();
    });
}

// Fetch alerts from the server
function fetchAlerts() {
    showLoading();
    fetch(`/alerts-api/?show_acknowledged=${showAcknowledged}`)
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                alerts = data.alerts;
                applyFilters();
            }
        })
        .catch(error => {
            console.error('Error fetching alerts:', error);
            showError('Failed to load alerts. Please try again later.');
        })
        .finally(() => {
            hideLoading();
        });
}

    function showLoading() {
        loadingSpinner.style.display = 'flex';
        alertsContainer.classList.add('loading');
    }

    function hideLoading() {
        loadingSpinner.style.display = 'none';
        alertsContainer.classList.remove('loading');
    }


    function applyFilters() {
        let filteredAlerts = [...alerts];

        // Apply severity filter
        if (filters.severity) {
            filteredAlerts = filteredAlerts.filter(alert => 
                alert.severity.toLowerCase() === filters.severity.toLowerCase()
            );
        }

        // Apply date filter
        const now = new Date();
        if (filters.timeRange !== 'all') {
            const timeRanges = {
                '24h': 24 * 60 * 60 * 1000,
                '7d': 7 * 24 * 60 * 60 * 1000,
                '30d': 30 * 24 * 60 * 60 * 1000
            };
            
            filteredAlerts = filteredAlerts.filter(alert => {
                const alertDate = new Date(alert.created_at);
                return (now - alertDate) <= timeRanges[filters.timeRange];
            });
        }

        updateAlertsTable(filteredAlerts);
    }

    function updateAlertsTable(alerts) {
        tableBody.innerHTML = '';
        
        if (alerts.length === 0) {
            emptyState.style.display = 'block';
            return;
        }

        emptyState.style.display = 'none';
        
        alerts.forEach(alert => {
            const row = document.createElement('tr');
            row.classList.add(`severity-${alert.severity.toLowerCase()}`);
            
            const severityIcon = getSeverityIcon(alert.severity);
            const formattedDate = formatDate(alert.created_at);
            
            row.innerHTML = `
                <td>
                    <div class="alert-name">
                        ${severityIcon}
                        <span>${alert.metric_name}</span>
                    </div>
                </td>
                <td>
                    <span class="severity-badge ${alert.severity.toLowerCase()}">${alert.severity}</span>
                </td>
                <td>
                    <time datetime="${alert.created_at}" title="${new Date(alert.created_at).toLocaleString()}">
                        ${formattedDate}
                    </time>
                </td>
                <td>
                    <a href="#" class="device-link" title="View device details">
                        ${alert.device_ip}
                    </a>
                </td>
                <td class="alert-details">
                    <span class="metric-value" title="Current Value">
                        <i class="fas fa-chart-line"></i>
                        ${alert.metric_value}% / ${alert.threshold_value}%
                    </span>
                </td>
                <td>
                    <button class="acknowledge-btn" 
                            data-alert-id="${alert.id}"
                            ${alert.is_acknowledged ? 'disabled' : ''}
                            aria-label="${alert.is_acknowledged ? 'Alert acknowledged' : 'Acknowledge alert'}">
                        <i class="fas ${alert.is_acknowledged ? 'fa-check-circle' : 'fa-check'}"></i>
                        ${alert.is_acknowledged ? 'Acknowledged' : 'Acknowledge'}
                    </button>
                </td>
            `;

            // event listener for acknowledge button
            const acknowledgeBtn = row.querySelector('.acknowledge-btn');
            if (acknowledgeBtn && !alert.is_acknowledged) {
                acknowledgeBtn.addEventListener('click', () => acknowledgeAlert(alert.id));
            }

            tableBody.appendChild(row);
        });
    }

    function acknowledgeAlert(alertId) {
        fetch(`/acknowledge-alert/${alertId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                fetchAlerts(); // Refresh the alerts
            }
        })
        .catch(console.error);
    }

    function getSeverityIcon(severity) {
        const icons = {
            'critical': '<i class="fas fa-exclamation-circle" style="color: #e53e3e;"></i>',
            'warning': '<i class="fas fa-exclamation-triangle" style="color: #ecc94b;"></i>',
            'info': '<i class="fas fa-info-circle" style="color: #4299e1;"></i>'
        };
        return icons[severity.toLowerCase()] || '';
    }

    function formatDate(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diff = now - date;
        
        // If less than 24 hours, show relative time
        if (diff < 24 * 60 * 60 * 1000) {
            const hours = Math.floor(diff / (60 * 60 * 1000));
            if (hours < 1) {
                const minutes = Math.floor(diff / (60 * 1000));
                return `${minutes} min${minutes !== 1 ? 's' : ''} ago`;
            }
            return `${hours} hour${hours !== 1 ? 's' : ''} ago`;
        }
        
        // Otherwise show the date
        return date.toLocaleDateString();
    }

    function getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') return value;
        }
        return '';
    }    function showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-error';
        errorDiv.role = 'alert';
        errorDiv.innerHTML = `
            <i class="fas fa-exclamation-circle"></i>
            <span>${message}</span>
            <button class="close-btn" aria-label="Close alert">×</button>
        `;
        
        const mainContent = document.querySelector('.main-content');
        const alertsHeader = document.querySelector('.alerts-header');
        
        if (mainContent && alertsHeader) {
            mainContent.insertBefore(errorDiv, alertsHeader);
        } else {
            // Fallback if elements aren't found
            document.body.insertBefore(errorDiv, document.body.firstChild);
        }

        // Auto-hide after 5 seconds
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }

    // Configure Thresholds button handler
    const configureBtn = document.getElementById('configureThresholdsBtn');
    if (configureBtn) {
        configureBtn.addEventListener('click', () => {
            window.location.href = '/thresholds/';
        });
    }

    // Initial load and periodic refresh
    fetchAlerts();
    const refreshInterval = setInterval(fetchAlerts, 30000); // Refresh every 30 seconds

    // Cleanup interval on page unload
    window.addEventListener('unload', () => {
        clearInterval(refreshInterval);
    });
});