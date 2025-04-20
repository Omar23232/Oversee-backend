document.addEventListener("DOMContentLoaded", function() {
    // Global variables for each chart
    let memoryChart, cpuChart, tempChart;

    // 1) Initialize all charts
    function initCharts() {
        // Memory Usage (Doughnut)
        const memoryCanvas = document.getElementById("memoryChart");
        if (memoryCanvas) {
            memoryChart = new Chart(memoryCanvas, {
                type: "doughnut",
                data: {
                    labels: ["Used", "Free"],
                    datasets: [{
                        data: [81, 19],
                        backgroundColor: ["#007bff", "#dcdcdc"],
                    }, ],
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

    // 4) (Optional) If you want a button to update the charts:
    const updateButton = document.getElementById("updateChartsBtn");
    if (updateButton) {
        updateButton.addEventListener("click", () => {
            updateMemoryChart(60, 40);
            updateCpuChart([25, 35, 45, 50, 30]);
            updateTempChart([40, 41, 43, 45, 46]);
        });
    }
});