const cpuChartCtx = document.getElementById('cpuChart').getContext('2d');
const ramChartCtx = document.getElementById('ramChart').getContext('2d');
const diskChartCtx = document.getElementById('diskChart').getContext('2d');
const gpuChartCtx = document.getElementById('gpuChart').getContext('2d');
const networkChartCtx = document.getElementById('networkChart').getContext('2d');

// --- Global Chart Nesneleri ---
let cpuChart, ramChart, diskChart, gpuChart, networkChart;

// --- Init Charts ---
function initCharts() {
    const neonColors = {
        cpu: '#ff0055',
        ram: '#00ffff',
        disk: '#ffcc00',
        gpu: '#00ff88',
        network: '#9966ff'
    };

    function createDoughnut(ctx, color) {
        return new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Usage', 'Free'],
                datasets: [{
                    data: [0, 100],
                    backgroundColor: [color, 'rgba(255,255,255,0.05)'],
                    borderColor: 'rgba(255,255,255,0.2)',
                    borderWidth: 2,
                    hoverOffset: 15
                }]
            },
            options: {
                responsive: true,
                cutout: '70%',
                plugins: { legend: { display: false } },
                animation: { animateRotate: true, animateScale: true }
            }
        });
    }

    cpuChart = createDoughnut(cpuChartCtx, neonColors.cpu);
    ramChart = createDoughnut(ramChartCtx, neonColors.ram);
    diskChart = createDoughnut(diskChartCtx, neonColors.disk);
    gpuChart = createDoughnut(gpuChartCtx, neonColors.gpu);

    networkChart = new Chart(networkChartCtx, {
        type: 'bar',
        data: {
            labels: ['Network (MB/s)'],
            datasets: [{
                label: 'Upload+Download',
                data: [0],
                backgroundColor: neonColors.network,
                borderRadius: 10
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true },
                x: { grid: { display: false } },
                yAxes: { grid: { color: 'rgba(255,255,255,0.1)' } }
            },
            animation: { duration: 800, easing: 'easeOutQuart' }
        }
    });
}

// --- Fetch ve Update ---
async function fetchData() {
    try {
        const res = await fetch('http://localhost:5000/data');
        const data = await res.json();

        const cpuUsage = data.cpu.usage;
        document.getElementById('cpuUsage').innerText = `CPU Usage: ${cpuUsage}%`;
        cpuChart.data.datasets[0].data = [cpuUsage, 100 - cpuUsage];
        cpuChart.update({ duration: 800, easing: 'easeOutQuart' });

        const ramUsage = data.ram.usage;
        const ramTotal = data.ram.total ? (data.ram.total / (1024 ** 3)).toFixed(2) : '---';
        document.getElementById('ramUsage').innerText = `RAM Usage: ${ramUsage}% / Total: ${ramTotal} GB`;
        ramChart.data.datasets[0].data = [ramUsage, 100 - ramUsage];
        ramChart.update({ duration: 800, easing: 'easeOutQuart' });

        let diskUsage = 0;
        if (data.disk instanceof Array && data.disk.length > 0) {
            const totalUsed = data.disk.reduce((acc, d) => acc + (d.used || 0), 0);
            const totalSize = data.disk.reduce((acc, d) => acc + (d.total || 1), 0);
            diskUsage = ((totalUsed / totalSize) * 100).toFixed(2);
        } else if (data.disk.usage) {
            diskUsage = data.disk.usage;
        }
        document.getElementById('diskUsage').innerText = `Disk Usage: ${diskUsage}%`;
        diskChart.data.datasets[0].data = [diskUsage, 100 - diskUsage];
        diskChart.update({ duration: 800, easing: 'easeOutQuart' });

        const gpuUsage = data.gpu.usage || 0;
        document.getElementById('gpuUsage').innerText = `GPU Usage: ${gpuUsage}%`;
        gpuChart.data.datasets[0].data = [gpuUsage, 100 - gpuUsage];
        gpuChart.update({ duration: 800, easing: 'easeOutQuart' });

        const gpuDevices = data.gpu.devices || [];
        const gpuDevicesContainer = document.getElementById('gpuDevices');
        gpuDevicesContainer.innerHTML = '';
        gpuDevices.forEach(device => {
            const div = document.createElement('div');
            div.className = 'gpu-device';
            div.innerHTML = `<strong>${device.name}</strong> - Usage: ${device.usage}% - Mem: ${device.memory_used}/${device.memory_total} MB`;
            gpuDevicesContainer.appendChild(div);
            gsap.fromTo(div, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.8, ease: "power3.out" });
        });

        const netSpeed = data.network.usage || 0;
        document.getElementById('networkUsage').innerText = `Network Speed: ${netSpeed} MB/s`;
        networkChart.data.datasets[0].data = [netSpeed];
        networkChart.update({ duration: 800, easing: 'easeOutQuart' });

        const sysLoad = data.system.load || 0;
        document.getElementById('systemLoad').innerText = `System Load: ${sysLoad}%`;

        gsap.fromTo(
            [cpuChart.canvas, ramChart.canvas, diskChart.canvas, gpuChart.canvas, networkChart.canvas],
            { boxShadow: '0 0 20px rgba(255,255,255,0.1)' },
            { boxShadow: '0 0 40px rgba(0,255,255,0.6)', duration: 1, repeat: -1, yoyo: true }
        );

    } catch (err) {
        console.error('Error fetching data', err);
    }
}

initCharts();
fetchData();
setInterval(fetchData, 2000);