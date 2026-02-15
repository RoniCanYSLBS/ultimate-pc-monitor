from flask import Flask, jsonify
from flask_cors import CORS
import psutil
import platform
import time

# GPU için platforma özel kütüphaneler
try:
    import GPUtil  # NVIDIA/AMD GPU
except ImportError:
    GPUtil = None

# pynvml NVML yoksa app çökmesin diye try-except
try:
    import pynvml  # NVIDIA GPU (opsiyonel)
    try:
        pynvml.nvmlInit()
    except pynvml.NVMLError_LibraryNotFound:
        print("⚠️ NVIDIA NVML kütüphanesi bulunamadı, GPU bilgisi sınırlı olacak.")
        pynvml = None
except ImportError:
    print("⚠️ pynvml modülü yok, NVIDIA GPU bilgisi alınamayacak.")
    pynvml = None

app = Flask(__name__)
CORS(app)  # Frontend'den veri çekmeye izin verir

prev_net = psutil.net_io_counters()
prev_time = time.time()

@app.route('/data')
def get_data():
    global prev_net, prev_time
    try:
        # -------- CPU ----------
        cpu_usage = psutil.cpu_percent(interval=0.1)

        # -------- RAM ----------
        ram_usage = psutil.virtual_memory().percent

        # -------- Disk ----------
        disk_total = 0
        disk_used = 0
        for part in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(part.mountpoint)
                disk_total += usage.total
                disk_used += usage.used
            except PermissionError:
                continue
        disk_usage = (disk_used / disk_total) * 100 if disk_total > 0 else 0

        # -------- GPU ----------
        gpu_usage = 0
        gpu_info = []

        # NVIDIA GPUtil
        if GPUtil:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu_usage = sum([gpu.load * 100 for gpu in gpus]) / len(gpus)
                for gpu in gpus:
                    gpu_info.append({
                        "name": gpu.name,
                        "usage": round(gpu.load * 100, 2),
                        "memory_total": round(gpu.memoryTotal, 2),
                        "memory_used": round(gpu.memoryUsed, 2),
                        "memory_free": round(gpu.memoryFree, 2)
                    })
        # NVIDIA pynvml
        elif pynvml:
            try:
                device_count = pynvml.nvmlDeviceGetCount()
                if device_count > 0:
                    total_load = 0
                    for i in range(device_count):
                        handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                        load = pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
                        total_load += load
                        mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                        gpu_info.append({
                            "name": f"GPU {i}",
                            "usage": load,
                            "memory_total": round(mem_info.total / (1024**2), 2),
                            "memory_used": round(mem_info.used / (1024**2), 2),
                            "memory_free": round(mem_info.free / (1024**2), 2)
                        })
                    gpu_usage = total_load / device_count
            except Exception:
                gpu_info.append({"name": "No GPU detected", "usage": 0, "memory_total": 0, "memory_used": 0, "memory_free": 0})
        # AMD + Intel Windows GPU (LibreHardwareMonitor ile)
        elif platform.system() == "Windows":
            try:
                import clr  # pythonnet
                DLL_PATH = r"C:\path\to\LibreHardwareMonitorLib.dll"  # DLL yolunu kendi sistemine göre değiştir
                clr.AddReference(DLL_PATH)
                from LibreHardwareMonitor import Hardware

                computer = Hardware.Computer()
                computer.GPUEnabled = True
                computer.Open()

                gpu_load_list = []

                for hw in computer.Hardware:
                    if hw.HardwareType.ToString() in ["GpuNvidia", "GpuAti", "GpuIntel"]:
                        hw.Update()
                        for sensor in hw.Sensors:
                            if sensor.SensorType.ToString() == "Load":
                                val = sensor.Value if sensor.Value is not None else 0
                                gpu_load_list.append(val)
                                gpu_info.append({
                                    "name": hw.Name,
                                    "usage": round(val, 2),
                                    "memory_total": 0,
                                    "memory_used": 0,
                                    "memory_free": 0
                                })
                if gpu_load_list:
                    gpu_usage = sum(gpu_load_list) / len(gpu_load_list)
            except Exception:
                gpu_info.append({"name": "No GPU detected", "usage": 0, "memory_total": 0, "memory_used": 0, "memory_free": 0})
        else:
            gpu_info.append({"name": "No GPU detected", "usage": 0, "memory_total": 0, "memory_used": 0, "memory_free": 0})

        # -------- Network ----------
        net_io = psutil.net_io_counters()
        current_time = time.time()
        delta_time = max(current_time - prev_time, 0.5)
        upload_speed = (net_io.bytes_sent - prev_net.bytes_sent) / (1024*1024) / delta_time
        download_speed = (net_io.bytes_recv - prev_net.bytes_recv) / (1024*1024) / delta_time
        network_speed = round(upload_speed + download_speed, 2)
        prev_net = net_io
        prev_time = current_time

        # -------- System load ----------
        system_load = cpu_usage

        # -------- JSON ---------
        data = {
            "cpu": {"usage": round(cpu_usage, 2)},
            "ram": {"usage": round(ram_usage, 2)},
            "disk": {"usage": round(disk_usage, 2)},
            "gpu": {"usage": round(gpu_usage, 2), "devices": gpu_info},
            "network": {"usage": network_speed},
            "system": {"load": round(system_load, 2)}
        }

    except Exception:
        data = {
            "cpu": {"usage": 0},
            "ram": {"usage": 0},
            "disk": {"usage": 0},
            "gpu": {"usage": 0, "devices": []},
            "network": {"usage": 0},
            "system": {"load": 0}
        }

    return jsonify(data)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)