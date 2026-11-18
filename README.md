# 🛸 Drone Camera Viewer (RTSP / UDP)

A lightweight, low-latency Python GUI application to stream live video feeds from common Wi-Fi FPV drones directly to your computer.

Built with **Python**, **OpenCV**, and **Tkinter**, this tool automates the UDP wake-up and heartbeat protocols required by many drone camera modules to unlock and maintain an RTSP video stream.

---

## 🎯 Supported & Tested Drones

Works with **most common Chinese Wi-Fi / FPV drones** utilizing standard UDP packet handshakes and RTSP streaming protocols.

### 🧪 Confirmed & Tested Models:
* **M3 MAX**
* **W5 MAX 4K**
* **J6 PRO Brushless**

*(And many other budget/toy drones utilizing similar onboard Wi-Fi camera modules and companion apps like WiFi-CAM, VS FPV, HF Drone, etc.)*

---

## ⚙️ How It Works

Many budget Wi-Fi drones do not expose an open RTSP stream immediately upon connecting. Instead, they require specific UDP packets to initialize the camera hardware and keep the video feed alive:

1. **Kickoff / Wake-up Packet**:
   - Sends `0xEF 0x00 0x04 0x00` via UDP to `192.168.169.1:8800` repeatedly every 100ms.
   - Signals the camera module to initialize and begin publishing the RTSP stream.

2. **Heartbeat / Keep-Alive Packet**:
   - Sends `0x01 0x01` via UDP to `192.168.1.1:7099` every 1 second.
   - Prevents the drone's camera server from timing out or shutting down the video pipeline.

3. **Low-Latency RTSP Capture**:
   - Connects to `rtsp://192.168.1.1:7070/webcam` via OpenCV (`cv2.CAP_FFMPEG`).
   - Uses a minimal buffer size (`CAP_PROP_BUFFERSIZE = 1`) to eliminate streaming lag and provide near real-time video monitoring.

4. **Dark-Themed GUI**:
   - Simple desktop interface built with Tkinter.
   - Start / Stop stream controls with real-time connection status indicators (`Idle`, `Connecting...`, `Live`, `Connection Failed`, `Stopped`).

---

## 📦 Requirements & Installation

### Prerequisites
- Python 3.8 or higher
- System Tkinter support:
  - **macOS / Windows**: Typically included with standard Python installations.
  - **Linux / Raspberry Pi**: `sudo apt install python3-tk`

### 1. Clone the Repository
```bash
git clone https://github.com/krishnakrish457/drone-camera-viewer
cd drone-camera-viewer
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

---

## 🚀 Usage Guide

1. **Power on your drone** and place it on a flat surface.
2. **Connect your computer's Wi-Fi** to the drone's access point:
   - Look for an open Wi-Fi network (typically named `FLOW-UFO`, `WiFi-FPV-XXXX`, `M3-XXXX`, `W5-XXXX`, etc.).
   - Make sure your operating system doesn't disconnect or switch networks due to "No Internet Connection".
3. **Run the viewer application**:
   ```bash
   python drone_viewer.py
   ```
4. Click **"Start Stream"** to begin packet transmission and view the live video feed.
5. Click **"Stop Stream"** when finished.

---

## 🛠️ Configuration & Customization

If your drone model uses different network parameters or subnets, you can easily tweak the settings directly at the top of `drone_viewer.py`:

```python
# --- Drone Network & Protocol Configuration ---
RTSP_URL = "rtsp://192.168.1.1:7070/webcam"

KICKOFF_IP = "192.168.169.1"
KICKOFF_PORT = 8800
KICKOFF_PAYLOAD = bytes([0xEF, 0x00, 0x04, 0x00])

HEARTBEAT_IP = "192.168.1.1"
HEARTBEAT_PORT = 7099
HEARTBEAT_PAYLOAD = bytes([0x01, 0x01])
```

- **RTSP URL**: Modify if your drone uses a different path or port (e.g., `rtsp://192.168.1.1:554/live/ch0`).
- **IP Subnet**: If your drone's gateway is `192.168.0.1` or `192.168.10.1`, adjust the IP targets accordingly.

---

## 🔍 Troubleshooting

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| **Status: Connection Failed** | Wi-Fi not connected to drone | Ensure your Wi-Fi interface is connected to the drone's SSID and not your home Wi-Fi. |
| **Multiple Network Adapters** | System routing UDP over Ethernet/Cellular | Disconnect other network adapters (or turn off mobile hotspot / Ethernet) so traffic routes through the drone's Wi-Fi interface. |
| **Firewall Blocking UDP** | Firewall preventing UDP outbound packets | Allow outbound UDP traffic on ports `8800` and `7099`. |
| **Stream Lag / Latency** | Wi-Fi signal interference | Keep the drone closer to the computer or check for channel congestion. |
| **OpenCV RTSP error** | Missing FFmpeg support in OpenCV | Install official OpenCV with FFmpeg support via `pip install --upgrade opencv-python`. |

---

## 📄 License

This project is open-source under the [MIT License](LICENSE).
