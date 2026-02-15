# System Monitoring Backend

![Backend Banner](https://img.shields.io/badge/Status-Active-success)

This is the backend server for a **real-time system monitoring dashboard**. It collects CPU, RAM, Disk, GPU, Network, and System Load data and serves it via a REST API.

---

## Features

-  CPU usage monitoring
-  RAM usage monitoring
-  Disk usage monitoring
-  GPU usage and device details
-  Network upload/download speed
-  Cross-platform support (Windows, Linux, macOS)
-  Real-time data via REST API
-  Automatic fallback if GPU libraries not found
-  Lightweight Flask backend

---

## Tech Stack

- **Python 3.10+**
- **Flask** – REST API server
- **psutil** – System metrics
- **GPUtil / pynvml** – GPU stats
- **Flask-CORS** – Enable frontend connections
- Optional: **LibreHardwareMonitor** on Windows for AMD/Intel GPU

---

## Installation

```bash
# Clone the repo
git clone https://github.com/yourusername/system-monitor-backend.git
cd system-monitor-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run server
python app.py

The API will run at: http://localhost:5000/data

API Response Example:
{
  "cpu": {"usage": 12.5},
  "ram": {"usage": 43.2},
  "disk": {"usage": 61.7},
  "gpu": {"usage": 21.3, "devices": [{"name": "NVIDIA RTX 3060", "usage": 21.3, "memory_total": 6144, "memory_used": 1320, "memory_free": 4824}]},
  "network": {"usage": 2.56},
  "system": {"load": 12.5}
}

