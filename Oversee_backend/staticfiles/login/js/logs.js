document.addEventListener('DOMContentLoaded', function() {
    // Toggle filters
    const toggleFilters = document.getElementById('toggleFilters');
    const filterOptions = document.getElementById('filterOptions');
    
    if (toggleFilters && filterOptions) {
        toggleFilters.addEventListener('click', function() {
            const isExpanded = toggleFilters.getAttribute('aria-expanded') === 'true';
            toggleFilters.setAttribute('aria-expanded', !isExpanded);
            filterOptions.hidden = isExpanded;
        });
    }

    // Export functionality
    const exportBtn = document.getElementById('exportLogs');
    if (exportBtn) {
        exportBtn.addEventListener('click', function() {
            // Create a CSV string
            const table = document.querySelector('.logs-table');
            if (!table) return;
            
            let csv = [];
            
            // Add headers
            let headers = [];
            table.querySelectorAll('th').forEach(header => {
                headers.push(header.textContent.trim());
            });
            csv.push(headers.join(','));
            
            // Add rows
            table.querySelectorAll('tbody tr').forEach(row => {
                let rowData = [];
                row.querySelectorAll('td').forEach((cell, index) => {
                    // Skip the details/actions column for command logs
                    if (index < headers.length) {
                        // For status cells, get the text content of the span
                        if (cell.querySelector('.log-level')) {
                            rowData.push('"' + cell.querySelector('.log-level').textContent.trim().replace(/"/g, '""') + '"');
                        } else {
                            // Remove any commas and wrap in quotes to handle special characters
                            rowData.push('"' + cell.textContent.trim().replace(/"/g, '""') + '"');
                        }
                    }
                });
                csv.push(rowData.join(','));
            });

            // Create and trigger download
            const csvContent = csv.join('\n');
            const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            const url = URL.createObjectURL(blob);
            link.setAttribute('href', url);
            
            // Set filename based on current log type
            const isCommandLogs = window.location.href.includes('log_type=commands');
            const filename = isCommandLogs ? 'command_logs.csv' : 'login_logs.csv';
            link.setAttribute('download', filename);
            
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        });
    }

    // Command output modal functionality
    const modal = document.getElementById('commandOutputModal');
    const outputButtons = document.querySelectorAll('.view-output-btn');
    const closeModal = document.querySelector('.close-modal');

    if (modal && outputButtons.length && closeModal) {
        // Close modal when clicking X
        closeModal.addEventListener('click', () => {
            modal.style.display = 'none';
        });

        // Close modal when clicking outside
        window.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });

        // Open modal and fetch command details
        outputButtons.forEach(btn => {
            btn.addEventListener('click', async () => {
                const commandId = btn.getAttribute('data-id');
                
                try {
                    // Add fetch command details endpoint
                    const response = await fetch(`/command-details/${commandId}/`);
                    const data = await response.json();
                    
                    if (data.status === 'success') {
                        document.getElementById('modalCommand').textContent = data.command;
                        document.getElementById('modalUser').textContent = data.user || 'Unknown';
                        document.getElementById('modalDevice').textContent = data.device_ip;
                        document.getElementById('modalTime').textContent = data.timestamp;
                        
                        // Format the JSON output
                        document.getElementById('commandOutputDisplay').textContent = 
                            JSON.stringify(data.output, null, 2);
                        
                        modal.style.display = 'block';
                    } else {
                        alert('Error loading command details');
                    }
                } catch (error) {
                    console.error('Error fetching command details:', error);
                    alert('Error loading command details');
                }
            });
        });
    }

    // Add filter functionality for command logs
    const commandSearch = document.getElementById('commandSearch');
    const userFilter = document.getElementById('userFilter');
    
    if (commandSearch) {
        commandSearch.addEventListener('input', filterCommandLogs);
    }
    
    if (userFilter) {
        userFilter.addEventListener('change', filterCommandLogs);
    }
    
    function filterCommandLogs() {
        const searchTerm = commandSearch.value.toLowerCase();
        const userSelected = userFilter.value.toLowerCase();
        
        document.querySelectorAll('.logs-table tbody tr').forEach(row => {
            const command = row.querySelector('td:nth-child(4)').textContent.toLowerCase();
            const user = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
            
            const matchesSearch = !searchTerm || command.includes(searchTerm);
            const matchesUser = !userSelected || user === userSelected;
            
            row.style.display = matchesSearch && matchesUser ? '' : 'none';
        });
    }
    
    // Add similar filter functionality for login logs
    const statusFilter = document.getElementById('statusFilter');
    const searchInput = document.getElementById('searchInput');
    
    if (statusFilter) {
        statusFilter.addEventListener('change', filterLoginLogs);
    }
    
    if (searchInput) {
        searchInput.addEventListener('input', filterLoginLogs);
    }
    
    function filterLoginLogs() {
        const status = statusFilter.value.toLowerCase();
        const searchTerm = searchInput.value.toLowerCase();
        
        document.querySelectorAll('.logs-table tbody tr').forEach(row => {
            const rowStatus = row.querySelector('td:nth-child(3) .log-level').textContent.toLowerCase();
            const username = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
            
            const matchesStatus = !status || rowStatus.includes(status);
            const matchesSearch = !searchTerm || username.includes(searchTerm);
            
            row.style.display = matchesStatus && matchesSearch ? '' : 'none';
        });
    }
});