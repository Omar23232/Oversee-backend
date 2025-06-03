document.addEventListener('DOMContentLoaded', function() {
    // Toggle filters
    const toggleFilters = document.getElementById('toggleFilters');
    const filterOptions = document.getElementById('filterOptions');
    
    toggleFilters.addEventListener('click', function() {
        const isExpanded = toggleFilters.getAttribute('aria-expanded') === 'true';
        toggleFilters.setAttribute('aria-expanded', !isExpanded);
        filterOptions.hidden = isExpanded;
    });

    // Export functionality
    document.getElementById('exportLogs').addEventListener('click', function() {
        // Create a CSV string
        const table = document.querySelector('.logs-table');
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
            row.querySelectorAll('td').forEach(cell => {
                // Remove any commas and wrap in quotes to handle special characters
                rowData.push('"' + cell.textContent.trim().replace(/"/g, '""') + '"');
            });
            csv.push(rowData.join(','));
        });

        // Create and trigger download
        const csvContent = csv.join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', 'login_logs.csv');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    });
});