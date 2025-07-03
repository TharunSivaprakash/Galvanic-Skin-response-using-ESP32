# Galvanic Skin Response (GSR) IoT Dashboard

This project is an **IoT-based GSR monitoring system** that captures real-time skin conductance data and visualizes emotional responses in a web dashboard.

An **ESP32 microcontroller** reads GSR sensor data and transmits it over Wi-Fi to a **Flask web server**, which logs the data, displays live plots, and enables session exports for analysis.

---

##  Features

- **Real-Time Data Acquisition**
  - Continuously collects GSR values from the ESP32 via Wi-Fi.
  - Logs timestamped readings in memory and optional CSV export.

- **Live Plotting**
  - Displays a live-updating chart of skin conductance levels.
  - Refreshes automatically without reloading the page.

- **Stimulus Presentation**
  - Shows an image or prompt while capturing responses.
  - Enables studying emotional or physiological reactions.

- **Data Export**
  - Downloads session data as CSV for further analysis.

---

## 🧩 Hardware Requirements

- **ESP32 Development Board**
- **GSR Sensor**
  - e.g., Grove GSR, or any analog conductance sensor.
- **USB Cable**
  - For ESP32 programming and power.

---

## ⚙️ Prerequisites

- **Python 3.8+**
- **Flask**
- **PySerial (if using serial fallback)**
- **NumPy**
- **Matplotlib**

---

## 💻 Installation

Clone this repository:

```bash
git clone https://github.com/yourusername/gsr-iot-dashboard.git
cd gsr-iot-dashboard
