import tkinter as tk
from tkinter import ttk


class MinimalUI:
    def __init__(self, root, app):
        self.root = root
        self.app = app

        # สีหลัก
        self.primary_color = "#3498db"  # สีน้ำเงิน
        self.success_color = "#2ecc71"  # สีเขียว
        self.danger_color = "#e74c3c"  # สีแดง
        self.bg_color = "#f5f5f5"  # สีพื้นหลัง

        # สร้าง UI components
        self.create_ui()

    def create_ui(self):
        """สร้าง UI แบบ minimal"""
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill="both", expand=True)

        # คำแนะนำ
        ttk.Label(frame, text="Minimal Fishing Bot", font=("Arial", 14, "bold")).pack(
            pady=5
        )
        ttk.Label(frame, text="Select region and press Start").pack(pady=5)

        # สถานะ
        status_frame = ttk.LabelFrame(frame, text="Status")
        status_frame.pack(fill="x", pady=5)

        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.pack(pady=5)

        self.region_label = ttk.Label(status_frame, text="No region selected")
        self.region_label.pack(pady=5)

        # ปุ่มควบคุม
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill="x", pady=5)

        self.select_button = ttk.Button(
            control_frame, text="Select Region", command=self.app.select_gauge_region
        )
        self.select_button.pack(side="left", padx=5)

        self.start_button = ttk.Button(
            control_frame,
            text="Start",
            command=self.app.start_fishing,
            state="disabled",
        )
        self.start_button.pack(side="left", padx=5)

        self.stop_button = ttk.Button(
            control_frame, text="Stop", command=self.app.stop_fishing, state="disabled"
        )
        self.stop_button.pack(side="left", padx=5)

        # เกจจำลอง
        gauge_frame = ttk.LabelFrame(frame, text="Gauge Visualization")
        gauge_frame.pack(fill="x", pady=5)

        self.gauge_canvas = tk.Canvas(
            gauge_frame, height=40, bg="#333333", highlightthickness=0
        )
        self.gauge_canvas.pack(fill="x", pady=5, padx=5)

        # สร้างเกจจำลอง
        self.create_gauge()

        # Hotkey info
        ttk.Label(
            frame, text="Press 'F10' to stop at any time", foreground="#e74c3c"
        ).pack(pady=5)

    def create_gauge(self):
        """สร้างเกจจำลอง"""
        # ความกว้างของ Canvas
        width = 380

        # สร้างโซนสีแดงซ้าย
        red_width = width * 0.2  # 20% ของความกว้าง
        self.gauge_red_left = self.gauge_canvas.create_rectangle(
            0, 0, red_width, 40, fill="#e74c3c", outline=""
        )

        # สร้างโซนสีเขียวกลาง
        self.gauge_green = self.gauge_canvas.create_rectangle(
            red_width, 0, width - red_width, 40, fill="#2ecc71", outline=""
        )

        # สร้างโซนสีแดงขวา
        self.gauge_red_right = self.gauge_canvas.create_rectangle(
            width - red_width, 0, width, 40, fill="#e74c3c", outline=""
        )

        # สร้างเส้นตัวชี้
        line_x = width / 2
        self.gauge_line = self.gauge_canvas.create_line(
            line_x, 0, line_x, 40, fill="white", width=2
        )

    def update_line_position(self, relative_pos):
        """อัปเดตตำแหน่งเส้นในเกจ"""
        width = self.gauge_canvas.winfo_width()
        if width < 10:
            width = 380

        line_x = width * relative_pos
        self.gauge_canvas.coords(self.gauge_line, line_x, 0, line_x, 40)

    def update_status(self, text, status_type="normal"):
        """อัปเดตข้อความสถานะ"""
        self.status_label.config(text=text)

        if status_type == "success":
            self.status_label.config(foreground="#2ecc71")
        elif status_type == "danger":
            self.status_label.config(foreground="#e74c3c")
        elif status_type == "warning":
            self.status_label.config(foreground="#f39c12")
        else:
            self.status_label.config(foreground="black")

    def update_region_info(self, region):
        """อัปเดตข้อมูลพื้นที่ที่เลือก"""
        if region:
            x1, y1, x2, y2 = region
            self.region_label.config(text=f"Region: ({x1}, {y1}) to ({x2}, {y2})")

    def set_start_button_state(self, state):
        """ตั้งค่าสถานะปุ่ม Start"""
        self.start_button.config(state=state)

    def set_button_states(self, select_state, start_state, stop_state):
        """ตั้งค่าสถานะของปุ่มทั้งหมด"""
        self.select_button.config(state=select_state)
        self.start_button.config(state=start_state)
        self.stop_button.config(state=stop_state)
