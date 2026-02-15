import psutil
import platform
import time
import socket

# Windows LibreHardwareMonitor GPU için
USE_LIBREHWM = platform.system() == "Windows"

if USE_LIBREHWM:
    try:
        import clr  # pythonnet
        DLL_PATH = r"C:\path\to\LibreHardwareMonitorLib.dll"  # DLL yolunu buraya yaz
        clr.AddReference(DLL_PATH)
        from LibreHardwareMonitor import Hardware
    except ImportError:
        print("⚠️ Uyarı: LibreHardwareMonitor import edilemedi, GPU bilgisi sınırlı olacak.")
        Hardware = None

def get_system_info():
    uname = platform.uname()
    return {
        "system": uname.system,
        "node_name": uname.node,
        "release": uname.release,
        "version": uname.version,
        "machine": uname.machine,
        "processor": uname.processor
    }

def get_cpu_info():
    return {
        "physical_cores": psutil.cpu_count(logical=False),
        "total_cores": psutil.cpu_count(logical=True),
        "max_frequency": psutil.cpu_freq().max,
        "min_frequency": psutil.cpu_freq().min,
        "current_frequency": psutil.cpu_freq().current,
        "usage_percent": psutil.cpu_percent(interval=1)
    }

def get_ram_info():
    svmem = psutil.virtual_memory()
    return {
        "total": svmem.total,
        "available": svmem.available,
        "used": svmem.used,
        "usage_percent": svmem.percent
    }

def get_disk_info():
    partitions = psutil.disk_partitions()
    disk_info = []
    for partition in partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disk_info.append({
                "device": partition.device,
                "mountpoint": partition.mountpoint,
                "fstype": partition.fstype,
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
                "usage_percent": usage.percent
            })
        except PermissionError:
            continue
    return disk_info

def get_network_info():
    net_io = psutil.net_io_counters()
    return {
        "bytes_sent": net_io.bytes_sent,
        "bytes_recv": net_io.bytes_recv,
        "packets_sent": net_io.packets_sent,
        "packets_recv": net_io.packets_recv
    }

def get_gpu_info():
    gpu_list = []

    if USE_LIBREHWM and Hardware:
        try:
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
                            gpu_list.append({
                                "id": hw.HardwareType.ToString(),
                                "name": hw.Name,
                                "driver": "",
                                "memory_total": 0,
                                "memory_used": 0,
                                "memory_free": 0,
                                "usage_percent": round(val, 2),
                                "temperature": 0
                            })
        except Exception:
            gpu_list.append({
                "id": -1,
                "name": "No GPU detected",
                "driver": "",
                "memory_total": 0,
                "memory_used": 0,
                "memory_free": 0,
                "usage_percent": 0,
                "temperature": 0
            })
    else:
        # Diğer platformlarda GPUtil ile
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            for gpu in gpus:
                gpu_list.append({
                    "id": gpu.id,
                    "name": gpu.name,
                    "driver": gpu.driver,
                    "memory_total": gpu.memoryTotal,
                    "memory_used": gpu.memoryUsed,
                    "memory_free": gpu.memoryFree,
                    "usage_percent": gpu.memoryUtil * 100,
                    "temperature": gpu.temperature
                })
        except ImportError:
            gpu_list.append({
                "id": -1,
                "name": "No GPU detected",
                "driver": "",
                "memory_total": 0,
                "memory_used": 0,
                "memory_free": 0,
                "usage_percent": 0,
                "temperature": 0
            })

    return gpu_list

def get_all_data():
    return {
        "system": get_system_info(),
        "cpu": get_cpu_info(),
        "ram": get_ram_info(),
        "disk": get_disk_info(),
        "network": get_network_info(),
        "gpu": get_gpu_info(),
        "timestamp": int(time.time())
    }

if __name__ == "__main__":
    import json
    print(json.dumps(get_all_data(), indent=4))