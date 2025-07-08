from flask import Flask, jsonify, render_template
import psutil
import platform
import os

try:
    import wmi
except ImportError:
    wmi = None

app = Flask(__name__)

# Função para temperatura da CPU
def get_cpu_temp():
    # Render (cloud) não possui sensores
    if os.environ.get("RENDER") == "true":
        return "N/A - Render"

    if platform.system() == "Windows" and wmi:
        c = wmi.WMI(namespace="root\\wmi")
        temps = c.MSAcpi_ThermalZoneTemperature()
        for temp in temps:
            return round((temp.CurrentTemperature / 10.0) - 273.15, 1)
    else:
        # Linux local: usando psutil
        temps = psutil.sensors_temperatures()
        if not temps:
            return "N/A"
        for name, entries in temps.items():
            for entry in entries:
                return entry.current
        return "N/A"

# Função para rotação do cooler
def get_fan_speed():
    if os.environ.get("RENDER") == "true":
        return "N/A - Render"

    # psutil não fornece fan speed; precisaria de lm-sensors + parsing
    return "Não implementado"

# Função para temperatura do disco
def get_disk_temp():
    if os.environ.get("RENDER") == "true":
        return "N/A - Render"
    
    # Exemplo Linux local com psutil
    temps = psutil.sensors_temperatures()
    if not temps:
        return "N/A"
    for name, entries in temps.items():
        for entry in entries:
            if 'nvme' in entry.label.lower() or 'hdd' in entry.label.lower():
                return entry.current
    return "N/A"

# Função para uso do disco
def get_disk_usage():
    usage = psutil.disk_usage('/')
    return {
        "used_percent": usage.percent,
        "free_gb": usage.free // (2**30)
    }

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/stats")
def stats():
    return jsonify({
        "cpu_temp": get_cpu_temp(),
        "fan_speed": get_fan_speed(),
        "disk_temp": get_disk_temp(),
        "disk_usage": get_disk_usage()
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # Define variavel RENDER se rodando no Render
    os.environ["RENDER"] = "true" if "RENDER" in os.environ else "false"
    app.run(debug=True, host="0.0.0.0", port=port)
