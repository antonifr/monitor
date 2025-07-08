from flask import Flask, jsonify, render_template
import psutil
import platform
import os

try:
    import wmi
except ImportError:
    wmi = None

app = Flask(__name__)

def get_cpu_temp():
    if platform.system() == "Windows" and wmi:
        c = wmi.WMI(namespace="root\\wmi")
        temps = c.MSAcpi_ThermalZoneTemperature()
        for temp in temps:
            return round((temp.CurrentTemperature / 10.0) - 273.15, 1)  # Kelvin to Celsius
    else:
        # Linux: usando 'sensors'
        try:
            temp = os.popen("sensors | grep 'Package id 0:' | awk '{print $4}'").read()
            temp = temp.strip().replace("+","").replace("°C","")
            return float(temp)
        except:
            return None

def get_fan_speed():
    if platform.system() == "Windows" and wmi:
        c = wmi.WMI(namespace="root\\wmi")
        fans = c.Win32_Fan()
        for fan in fans:
            return fan.DesiredSpeed
    else:
        # Linux: usando 'sensors'
        fan = os.popen("sensors | grep fan | awk '{print $2}'").read()
        return fan.strip()

def get_disk_temp():
    # Exemplo Linux com hddtemp
    temp = os.popen("hddtemp /dev/sda | awk '{print $NF}'").read()
    return temp.strip()

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
    app.run(debug=True, host="0.0.0.0")
