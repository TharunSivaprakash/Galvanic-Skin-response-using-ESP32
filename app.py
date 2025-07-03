from flask import Flask, Response, render_template_string
import serial
import serial.tools.list_ports
import time
import json
import csv
from io import StringIO
from datetime import datetime

app = Flask(__name__)

# Store GSR data with timestamps for CSV
data_log = []

# Try to auto-detect ESP32 serial port
def find_serial_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "ESP32" in port.description or "CH340" in port.description or "USB" in port.description:
            return port.device
    return None

# Serial port configuration
SERIAL_PORT = find_serial_port() or 'COM5'
BAUD_RATE = 115200

# Initialize serial connection
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
except serial.SerialException:
    print(f"Error: Could not open port {SERIAL_PORT}. Check port name and connections.")
    exit(1)

# HTML template for full-screen ApexCharts line graph and CSV download
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <title>GSR Sensor Dashboard</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { 
      font-family: Arial, sans-serif; 
      margin: 0; 
      padding: 0; 
      background-color: #f0f0f0; 
      display: flex; 
      flex-direction: column; 
      height: 100vh; 
      overflow: hidden; 
    }
    .container { 
      flex: 1; 
      display: flex; 
      flex-direction: column; 
      align-items: center; 
      justify-content: center; 
      width: 100vw; 
    }
    h1 { 
      color: #333; 
      margin: 10px 0; 
      font-size: 24px; 
    }
    .port-message { 
      font-size: 16px; 
      color: #0066cc; 
      margin: 5px 0; 
    }
    .chart-container { 
      width: 100vw; 
      height: calc(100vh - 90px); /* Space for header and button */
    }
    #gsrChart { 
      width: 100% !important; 
      height: 100% !important; 
    }
    .download-btn { 
      padding: 8px 16px; 
      background-color: #007BFF; 
      color: white; 
      border: none; 
      border-radius: 5px; 
      cursor: pointer; 
      margin: 10px 0; 
      font-size: 14px; 
    }
    .download-btn:hover { 
      background-color: #0056b3; 
    }
  </style>
  <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
</head>
<body>
  <div class="container">
    <h1>GSR Sensor Dashboard</h1>
    <p class="port-message">Connected to port: {{ serial_port }}</p>
    <div class="chart-container">
      <div id="gsrChart"></div>
    </div>
    <button class="download-btn" onclick="window.location.href='/download_csv'">Download CSV</button>
  </div>
<script>
  // Initialize ApexCharts
  const options = {
    chart: {
      type: 'area',
      height: '100%',
      animations: { enabled: false }, // Disable animations for speed
      toolbar: { show: false },
      zoom: { enabled: false }
    },
    series: [{
      name: 'GSR Value',
      data: []
    }],
    xaxis: {
      title: { text: 'Time (Samples)', style: { fontSize: '12px' } },
      range: 100, // Show last 100 samples
      labels: { show: true, rotate: 0, style: { fontSize: '10px' } }
    },
    yaxis: {
      title: { text: 'GSR Reading (ADC)', style: { fontSize: '12px' } },
      min: 0,
      max: 4095,
      labels: { style: { fontSize: '10px' } }
    },
    title: {
      text: 'Real-Time GSR Sensor Data',
      align: 'center',
      style: { fontSize: '14px' }
    },
    colors: ['#007BFF'],
    fill: {
      type: 'gradient',
      gradient: {
        shadeIntensity: 1,
        opacityFrom: 0.1,
        opacityTo: 0.3,
        stops: [0, 100]
      }
    },
    stroke: { width: 1.5, curve: 'straight' },
    grid: { borderColor: '#ccc', opacity: 0.3 },
    dataLabels: { enabled: false }
  };

  const chart = new ApexCharts(document.querySelector("#gsrChart"), options);
  chart.render();

  let sampleCount = 0;
  let rawData = [];
  const smoothingWindow = 3; // For light fluctuation detection

  const source = new EventSource('/events');
  source.onmessage = function(event) {
    const eventData = JSON.parse(event.data);
    if (eventData.error) {
      console.error(eventData.error);
      return;
    }

    rawData.push(eventData.gsr);
    if (rawData.length > smoothingWindow) {
      rawData.shift();
    }

    const smoothedValue = rawData.reduce((a, b) => a + b, 0) / rawData.length;

    chart.appendData([{ data: [{ x: sampleCount++, y: smoothedValue }] }]);

    if (sampleCount > 100) {
      chart.updateOptions({
        xaxis: { range: 100, min: sampleCount - 100, max: sampleCount }
      });
    }
  };
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, serial_port=SERIAL_PORT)

@app.route('/events')
def sse():
    def generate():
        while True:
            try:
                if ser.in_waiting > 0:
                    data = ser.readline().decode('utf-8').strip()
                    try:
                        gsr = int(data)
                        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                        data_log.append({'timestamp': timestamp, 'gsr': gsr})
                        yield f"data: {json.dumps({'gsr': gsr})}\n\n"
                    except ValueError:
                        print(f"Invalid data received: {data}")
            except serial.SerialException:
                print("Serial connection lost.")
                yield f"data: {json.dumps({'error': 'Serial connection lost'})}\n\n"
                break
            time.sleep(0.2)  # Match ESP32's 200ms interval
    return Response(generate(), mimetype='text/event-stream')

@app.route('/download_csv')
def download_csv():
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['Timestamp', 'GSR Value'])
    for entry in data_log:
        writer.writerow([entry['timestamp'], entry['gsr']])
    output = si.getvalue()
    si.close()
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=gsr_data.csv"}
    )

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        ser.close()