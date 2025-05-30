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

    function updateCPUStats() {
        fetch('/cpu-stats/')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Update numeric displays
                    document.getElementById('cpu-5s').textContent = `${data.five_seconds}%`;
                    document.getElementById('cpu-1m').textContent = `${data.one_minute}%`;
                    document.getElementById('cpu-5m').textContent = `${data.five_minutes}%`;
                    
                    // Update line chart
                    updateCpuChart([
                        data.five_seconds,
                        data.one_minute,
                        data.five_minutes
                    ]);
                }
            });
    }
    // 3) Fetch and update uptime data
    function pollUptime() {
    fetch('/uptime-api/')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success' && typeof data.output === 'object') {
                document.getElementById('uptime-days').textContent = data.output.days ?? '-';
                document.getElementById('uptime-hours').textContent = data.output.hours ?? '-';
                document.getElementById('uptime-minutes').textContent = data.output.minutes ?? '-';
                document.getElementById('uptime-seconds').textContent = data.output.seconds ?? '-';
                document.getElementById('uptime-timestamp').textContent = `Last checked: ${data.timestamp}`;
            }
        })
        .catch(console.error);
    }

    // 4) Polling for interface states
    function pollInterfaceStates() {
    fetch('/interface-api/')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success' && Array.isArray(data.interfaces)) {
                const upCount = data.interfaces.filter(i => i.status === 'up').length;
                const downCount = data.interfaces.filter(i => i.status === 'lower-layer-down').length;
                document.getElementById('interfaces-up-count').textContent = upCount;
                document.getElementById('interfaces-down-count').textContent = downCount;
            }
        })
        .catch(console.error);
}

    function updateInterfaceDisplay(interfaces) {
    const container = document.getElementById('interface-status-container');
    container.innerHTML = interfaces.map(intf => `
        <div class="card metric-card interface-card">
            <h4>${intf.name}</h4>
            <p>Status: <span class="status-badge ${intf.status === 'up' ? 'status-up' : 'status-down'}">${intf.status}</span></p>
            <p>MAC: <span>${intf.mac}</span></p>
            <small>Last change: ${intf.last_change}</small>
        </div>
    `).join('');
}
    // event listener to the button
    const btn = document.getElementById('show-interfaces-btn');
        if (btn) {
            btn.addEventListener('click', function() {
                window.location.href = '/interfaces/';
            });
        }

    //  Start polling 
    function startPolling() {
    
    // Initial loads
    fetchMemoryStats();
    setInterval(fetchMemoryStats, 60000); // Memory every 20s

    updateCPUStats();
    setInterval(updateCPUStats, 60000);    // CPU every 3s

    pollUptime();
    setInterval(pollUptime, 60000); // Uptime every 50s

    pollInterfaceStates(); // Initial call
    setInterval(pollInterfaceStates, 50000);
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

    // Add to your existing code
   
  
    
});