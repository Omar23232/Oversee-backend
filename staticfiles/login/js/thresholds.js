document.addEventListener('DOMContentLoaded', function() {
    const thresholdForm = document.getElementById('thresholdForm');
    const thresholdsTableBody = document.getElementById('thresholdsTableBody');

    // Function to fetch and display thresholds
    function fetchThresholds() {
        fetch('/thresholds-api/')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    updateThresholdsTable(data.thresholds);
                }
            })
            .catch(console.error);
    }

    // Function to update thresholds table
    function updateThresholdsTable(thresholds) {
        thresholdsTableBody.innerHTML = '';

        thresholds.forEach(threshold => {
            const row = document.createElement('tr');
            
            // Format metric name for display
            let metricDisplay = threshold.metric.replace('_', ' ');
            metricDisplay = metricDisplay.charAt(0).toUpperCase() + metricDisplay.slice(1);
            
            row.innerHTML = `
                <td>${metricDisplay}</td>
                <td>${threshold.threshold_value}%</td>
                <td class="severity-${threshold.severity.toLowerCase()}">${threshold.severity}</td>
                <td>
                    <button class="delete-btn" data-id="${threshold.id}">Delete</button>
                </td>
            `;
            
            thresholdsTableBody.appendChild(row);
        });

        // Add event listeners for delete buttons
        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                if (confirm('Are you sure you want to delete this threshold?')) {
                    deleteThreshold(this.dataset.id);
                }
            });
        });
    }

    // Function to delete a threshold
    function deleteThreshold(id) {
        fetch('/thresholds-api/', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ id: id })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                fetchThresholds();
            }
        })
        .catch(console.error);
    }

    // Handle form submission
    thresholdForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const threshold = {
            metric: document.getElementById('metric').value,
            threshold_value: parseFloat(document.getElementById('threshold-value').value),
            severity: document.getElementById('severity').value
        };
        
        fetch('/thresholds-api/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(threshold)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                thresholdForm.reset();
                fetchThresholds();
            }
        })
        .catch(console.error);
    });

    // Helper function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Initial load of thresholds
    fetchThresholds();
});