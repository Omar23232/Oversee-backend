document.addEventListener('DOMContentLoaded', function() {
    // Add keyboard navigation for device rows
    const deviceRows = document.querySelectorAll('.device-row');
    deviceRows.forEach(row => {
        row.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                const commandBtn = row.querySelector('.btn-command');
                if (commandBtn) {
                    commandBtn.click();
                }
            }
        });
    });

    // Handle tooltips for mobile devices
    if ('ontouchstart' in window) {
        const tooltips = document.querySelectorAll('[data-tooltip]');
        tooltips.forEach(element => {
            element.addEventListener('click', (e) => {
                const tooltip = element.getAttribute('data-tooltip');
                const existingTooltip = document.querySelector('.mobile-tooltip');
                if (existingTooltip) {
                    existingTooltip.remove();
                }

                const tooltipElement = document.createElement('div');
                tooltipElement.className = 'mobile-tooltip';
                tooltipElement.textContent = tooltip;
                document.body.appendChild(tooltipElement);

                setTimeout(() => {
                    tooltipElement.remove();
                }, 2000);
            });
        });
    }

    // Add loading state for actions
    const actionButtons = document.querySelectorAll('.btn');
    actionButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            btn.classList.add('loading');
        });
    });

    // Optional: Add device status update functionality
    function updateDeviceStatuses() {
        const statusElements = document.querySelectorAll('[role="status"]');
        const loadingOverlay = document.getElementById('loadingOverlay');
        
        if (loadingOverlay) {
            loadingOverlay.hidden = false;
        }

        // Simulated API call - replace with actual API endpoint
        setTimeout(() => {
            statusElements.forEach(status => {
                // Update status based on API response
                const currentStatus = status.textContent.trim().toLowerCase();
                const newStatus = currentStatus === 'up' ? 'down' : 'up';
                
                status.className = `status-${newStatus}`;
                status.textContent = newStatus.charAt(0).toUpperCase() + newStatus.slice(1);
                status.setAttribute('aria-label', `Device status: ${newStatus}`);
            });

            if (loadingOverlay) {
                loadingOverlay.hidden = true;
            }
        }, 2000);
    }

    // Update statuses periodically (every 30 seconds)
    // Uncomment to enable automatic status updates
    // setInterval(updateDeviceStatuses, 30000);
});
