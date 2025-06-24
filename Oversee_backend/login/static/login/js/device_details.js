document.addEventListener('DOMContentLoaded', function() {
    // Initialize Memory Chart
    const memoryCanvas = document.getElementById('memoryChart');
    if (memoryCanvas) {
        const memoryPercentage = parseFloat(document.getElementById('memory-percentage').textContent);
        const memoryChart = new Chart(memoryCanvas, {
            type: 'doughnut',
            data: {                labels: ['Used', 'Free'],
                datasets: [{
                    data: [memoryPercentage, 100 - memoryPercentage],
                    backgroundColor: ['#001F3F', '#6A9AB0'],
                    borderWidth: 0,
                    cutout: '75%'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ' + context.raw + '%';
                            }
                        }
                    }
                }
            }
        });
    }

    // Initialize CPU Chart
    const cpuCanvas = document.getElementById('cpuChart');
    if (cpuCanvas) {
        // Get CPU values if they exist
        const cpuValues = [];
        const cpuLabels = [];
        
        document.querySelectorAll('.metric-item').forEach(item => {
            const label = item.querySelector('.metric-label');
            const value = item.querySelector('.metric-value');
            
            if (label && value && (
                label.textContent.includes('5 Seconds') || 
                label.textContent.includes('1 Minute') || 
                label.textContent.includes('5 Minutes')
            )) {
                cpuLabels.push(label.textContent);
                cpuValues.push(parseFloat(value.textContent));
            }
        });
        
        if (cpuValues.length > 0) {
            const cpuChart = new Chart(cpuCanvas, {
                type: 'bar',
                data: {
                    labels: cpuLabels,                    datasets: [{
                        label: 'CPU Usage',
                        data: cpuValues,
                        backgroundColor: '#001F3F',
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            ticks: {
                                callback: function(value) {
                                    return value + '%';
                                }
                            }
                        }
                    }
                }
            });
        }
    }

    // Function to periodically refresh data
    function setupDataRefresh() {
        // We could add AJAX calls here to refresh the data periodically
        // For example, to update memory usage, CPU stats, etc.
        /*
        const deviceId = window.location.pathname.split('/')[2];
        
        setInterval(() => {
            fetch(`/api/devices/${deviceId}/stats/`)
                .then(response => response.json())
                .then(data => {
                    // Update memory chart
                    // Update CPU chart
                    // Update interface status
                })
                .catch(error => console.error('Error fetching device stats:', error));
        }, 30000); // Refresh every 30 seconds
        */
    }

    // Call the setup function
    setupDataRefresh();
});