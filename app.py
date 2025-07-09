from flask import Flask, jsonify, render_template
import psutil
import platform
import os
import subprocess

try:
    import wmi
except ImportError:
    wmi = None

app = Flask(__name__)

# Função para temperatura da CPU
def get_cpu_temp():
    if os.environ.get("RENDER") == "true":
        return "N/A - Render"

    if platform.system() == "Windows" and wmi:
        c = wmi.WMI(namespace="root\\wmi")
        temps = c.MSAcpi_ThermalZoneTemperature()
        for temp in temps:
            return round((temp.CurrentTemperature / 10.0) - 273.15, 1)
    else:
        try:
            temps = psutil.sensors_temperatures()
            if not temps:
                return "N/A"
            for name, entries in temps.items():
                for entry in entries:
                    return entry.current
            return "N/A"
        except Exception as e:
            return str(e)

# Função para rotação do cooler
def get_fan_speed():
    if os.environ.get("RENDER") == "true":
        return "N/A - Render"

    try:
        output = subprocess.check_output(["sensors"]).decode()
        for line in output.splitlines():
            if "fan" in line.lower():
                return line.strip()
        return "N/A"
    except Exception as e:
        return str(e)

# Função para temperatura do disco
def get_disk_temp():
    if os.environ.get("RENDER") == "true":
        return "N/A - Render"

    try:
        temps = psutil.sensors_temperatures()
        if not temps:
            return "N/A"
        for name, entries in temps.items():
            for entry in entries:
                label = entry.label.lower()
                if 'nvme' in label or 'hdd' in label or 'ssd' in label:
                    return entry.current
        return "N/A"
    except Exception as e:
        return str(e)

# Função para uso do disco
def get_disk_usage():
    usage = psutil.disk_usage('/')
    return {
        "used_percent": usage.percent,
        "free_gb": usage.free // (2**30)
    }

# Função para uso de CPU
def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

# Função para uso de memória
def get_memory_usage():
    return psutil.virtual_memory().percent

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/stats")
def stats():
    return jsonify({
        "cpu_temp": get_cpu_temp(),
        "fan_speed": get_fan_speed(),
        "disk_temp": get_disk_temp(),
        "disk_usage": get_disk_usage(),
        "cpu_usage": get_cpu_usage(),
        "memory_usage": get_memory_usage()
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    if "RENDER" not in os.environ:
        os.environ["RENDER"] = "false"
    app.run(debug=True, host="0.0.0.0", port=port)
