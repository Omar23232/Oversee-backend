// ddos_alerts.js - JavaScript for DDoS Alerts page

document.addEventListener('DOMContentLoaded', function() {
    // Initialize variables
    let lastUpdateTime = new Date();
    let detectionInterval;

    // Get DOM elements for updates
    const lastScanTimeElement = document.getElementById('lastScanTime');
    const threatLevelElement = document.getElementById('currentThreatLevel');
    const totalAttacksElement = document.getElementById('totalAttacksBlocked');
    const activeAttacksElement = document.getElementById('activeAttacks');
    const mitigatedAttacksElement = document.getElementById('mitigatedAttacks');
    const resolvedAttacksElement = document.getElementById('resolvedAttacks');
    const alertsTableBody = document.getElementById('ddosAlertsTableBody');
    const emptyState = document.getElementById('emptyState');
    const alertsTable = document.querySelector('.alerts-table');

    // Start monitoring for DDoS attacks
    startDetection();

    // Event listeners for filter controls
    const timeRangeFilter = document.getElementById('timeRangeFilter');
    const showResolvedCheckbox = document.getElementById('showResolvedCheckbox');
    
    if (timeRangeFilter) {
        timeRangeFilter.addEventListener('change', function() {
            console.log('Time range changed to:', this.value);
        });
    }
    
    if (showResolvedCheckbox) {
        showResolvedCheckbox.addEventListener('change', function() {
            // Will be implemented to show/hide resolved alerts
            console.log('Show resolved:', this.checked);
        });
    }

    // Function to start detection interval
    function startDetection() {
        if (detectionInterval) {
            clearInterval(detectionInterval);
        }

        checkForAttacks();

        detectionInterval = setInterval(checkForAttacks, 3000);
    }

    // Function to check for DDoS attacks via API
    function checkForAttacks() {
        fetch('/ddos-model/')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {;
                updateLastScanTime();
            })
            .catch(error => {
                console.error('Error checking for DDoS attacks:', error);
            });
    }

    // Update the last scan time
    function updateLastScanTime() {
        lastUpdateTime = new Date();
        if (lastScanTimeElement) {
            lastScanTimeElement.textContent = formatTime(lastUpdateTime);
        }
    }

    // Format time for display
    function formatTime(date) {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    }

    // Add event listener for Block button
    const blockButtons = document.querySelectorAll('.block-btn');

    blockButtons.forEach(button => {
        button.addEventListener('click', function() {
            const alertId = this.dataset.alertId;

            // Send request to backend to update alert status
            fetch(`/update-alert-status/${alertId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ status: 'resolved' }),
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to update alert status');
                }
                return response.json();
            })
            .then(data => {
                // Update UI to reflect resolved status
                const row = this.closest('tr');
                const statusBadge = row.querySelector('.status-badge');
                statusBadge.textContent = 'Resolved';
                statusBadge.classList.remove('active');
                statusBadge.classList.add('resolved');

                // Remove Block button
                this.remove();
            })
            .catch(error => {
                console.error('Error updating alert status:', error);
            });
        });
    });

    // Cleanup interval when page is unloaded
    window.addEventListener('beforeunload', function() {
        if (detectionInterval) {
            clearInterval(detectionInterval);
        }
    });
});
