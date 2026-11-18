import socket
import threading
import time
import tkinter as tk
from PIL import Image, ImageTk
import cv2

# --- Drone Network & Protocol Configuration ---
RTSP_URL = "rtsp://192.168.1.1:7070/webcam"

KICKOFF_IP = "192.168.169.1"
KICKOFF_PORT = 8800
KICKOFF_PAYLOAD = bytes([0xEF, 0x00, 0x04, 0x00])

HEARTBEAT_IP = "192.168.1.1"
HEARTBEAT_PORT = 7099
HEARTBEAT_PAYLOAD = bytes([0x01, 0x01])


class DroneViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Drone Camera Viewer")
        self.root.configure(bg="#1e1e1e")
        self.root.resizable(False, False)

        self.running = threading.Event()
        self.frame_lock = threading.Lock()
        self.latest_frame = None

        # --- Video Display Area ---
        self.video_label = tk.Label(
            root,
            text="Stream Stopped",
            fg="#888888",
            bg="#121212",
            font=("Segoe UI", 14),
            width=80,
            height=24,
        )
        self.video_label.pack(padx=12, pady=(12, 8))

        # --- Bottom Controls ---
        controls = tk.Frame(root, bg="#1e1e1e")
        controls.pack(fill=tk.X, padx=12, pady=(0, 12))

        self.start_btn = tk.Button(
            controls,
            text="Start Stream",
            command=self.start_stream,
            bg="#27ae60",
            fg="white",
            activebackground="#2ecc71",
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            padx=16,
            pady=6,
            cursor="hand2",
        )
        self.start_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.stop_btn = tk.Button(
            controls,
            text="Stop Stream",
            command=self.stop_stream,
            bg="#c0392b",
            fg="white",
            activebackground="#e74c3c",
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            padx=16,
            pady=6,
            state=tk.DISABLED,
            cursor="hand2",
        )
        self.stop_btn.pack(side=tk.LEFT)

        self.status_var = tk.StringVar(value="Status: Idle")
        tk.Label(
            controls,
            textvariable=self.status_var,
            fg="#cccccc",
            bg="#1e1e1e",
            font=("Segoe UI", 10),
        ).pack(side=tk.RIGHT)

        self.update_gui()

    # --- Background UDP & Capture Workers ---
    def _kickoff_worker(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while self.running.is_set():
            try:
                sock.sendto(KICKOFF_PAYLOAD, (KICKOFF_IP, KICKOFF_PORT))
            except Exception:
                pass
            time.sleep(0.1)
        sock.close()

    def _heartbeat_worker(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while self.running.is_set():
            try:
                sock.sendto(HEARTBEAT_PAYLOAD, (HEARTBEAT_IP, HEARTBEAT_PORT))
            except Exception:
                pass
            time.sleep(1.0)
        sock.close()

    def _capture_worker(self):
        time.sleep(0.5)  # Allow kickoff packets to wake the camera first
        cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        if not cap.isOpened():
            self.root.after(0, self._on_connect_failed)
            return

        self.root.after(0, lambda: self.status_var.set("Status: Live"))

        while self.running.is_set():
            ret, frame = cap.read()
            if ret:
                with self.frame_lock:
                    self.latest_frame = frame
            else:
                time.sleep(0.01)

        cap.release()

    # --- Button Actions ---
    def start_stream(self):
        if self.running.is_set():
            return

        self.running.set()
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_var.set("Status: Connecting...")
        self.video_label.config(text="Connecting to drone...", image="")

        threading.Thread(target=self._kickoff_worker, daemon=True).start()
        threading.Thread(target=self._heartbeat_worker, daemon=True).start()
        threading.Thread(target=self._capture_worker, daemon=True).start()

    def stop_stream(self):
        self.running.clear()
        with self.frame_lock:
            self.latest_frame = None

        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_var.set("Status: Stopped")
        self.video_label.config(image="", text="Stream Stopped", width=80, height=24)

    def _on_connect_failed(self):
        self.stop_stream()
        self.status_var.set("Status: Connection Failed")

    # --- UI Frame Refresh Loop ---
    def update_gui(self):
        if self.running.is_set():
            frame = None
            with self.frame_lock:
                if self.latest_frame is not None:
                    frame = self.latest_frame.copy()

            if frame is not None:
                frame = cv2.resize(frame, (640, 480))
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                imgtk = ImageTk.PhotoImage(image=Image.fromarray(rgb))
                self.video_label.imgtk = imgtk
                self.video_label.config(image=imgtk, text="", width=640, height=480)

        self.root.after(20, self.update_gui)

    def on_close(self):
        self.running.clear()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = DroneViewerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
