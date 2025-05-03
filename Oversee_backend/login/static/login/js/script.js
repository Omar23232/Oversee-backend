document.addEventListener("DOMContentLoaded", function() {
    // Global variables for each chart
    let memoryChart, cpuChart, tempChart;
    
    // Format bytes to MB/GB
    function formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i]);
    }

    // 1) Initialize all charts
    function initCharts() {
        // Memory Usage (Doughnut) - Start with empty data
        const memoryCanvas = document.getElementById("memoryChart");
        if (memoryCanvas) {
            memoryChart = new Chart(memoryCanvas, {
                type: "doughnut",
                data: {
                    labels: ["Used", "Free"],
                    datasets: [{
                        data: [0, 100], // Initial state
                        backgroundColor: ["#007bff", "#dcdcdc"],
                    }],
                },
                options: {
                    cutout: "70%",
                },
            });
        }

        // CPU Usage (Line Chart)
        const cpuCanvas = document.getElementById("cpuChart");
        if (cpuCanvas) {
            cpuChart = new Chart(cpuCanvas, {
                type: "line",
                data: {
                    labels: ["0s", "10s", "20s", "30s", "40s"],
                    datasets: [{
                        label: "CPU",
                        data: [30, 40, 35, 50, 45],
                        borderColor: "#f39c12",
                        fill: false,
                    }, ],
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                },
            });
        }

        // Temperature (Bar Chart)
        const tempCanvas = document.getElementById("tempChart");
        if (tempCanvas) {
            tempChart = new Chart(tempCanvas, {
                type: "bar",
                data: {
                    labels: ["10 AM", "11 AM", "12 PM", "1 PM", "2 PM"],
                    datasets: [{
                        label: "Temperature (°C)",
                        data: [42, 44, 45, 43, 46],
                        backgroundColor: "#ffce54",
                    }, ],
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                },
            });
        }
    }

    // 2) Fetch and update memory data
    function fetchMemoryStats() {
        fetch('/memory-stats/')  // Your Django API endpoint
            .then(response => response.json())
            .then(data => {
                // Update the chart
                const freePercent = 100 - data.used_percentage;
                updateMemoryChart(data.used_percentage, freePercent);
                
                // Update the numeric display
                document.querySelector('.chart-value').textContent = `${data.used_percentage}%`;
                
                // Update the details
                const detailsHTML = `
                    <p>Total: ${formatBytes(data.total)} GB</p>
                    <p>Used: ${formatBytes(data.used)} MB</p>
                    <p>Updated: ${data.timestamp}</p>
                    `;
                document.querySelector('.memory-details').innerHTML = detailsHTML;
            })
            .catch(error => console.error('Error fetching memory stats:', error));
    }

    // 3) Start polling (every 3 seconds)
    function startPolling() {
        fetchMemoryStats(); // Initial load
        setInterval(fetchMemoryStats, 5000); // Subsequent polls
    }

    // Initialize everything
    initCharts();
    startPolling();
    
    // 2) Functions to update each chart's data later
    function updateMemoryChart(used, free) {
        if (memoryChart) {
            memoryChart.data.datasets[0].data = [used, free];
            memoryChart.update();
        }
    }

    function updateCpuChart(newDataArray) {
        if (cpuChart) {
            cpuChart.data.datasets[0].data = newDataArray;
            cpuChart.update();
        }
    }

    function updateTempChart(newDataArray) {
        if (tempChart) {
            tempChart.data.datasets[0].data = newDataArray;
            tempChart.update();
        }
    }

    // 3) Initialize all charts on page load
    initCharts();

    
});