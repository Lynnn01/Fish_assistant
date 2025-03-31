import tkinter as tk
from tkinter import ttk
import time
import threading


class EnhancedUI:
    def __init__(self, root, app):
        self.root = root
        self.app = app

        # สีหลัก
        self.primary_color = "#3498db"  # สีน้ำเงิน
        self.success_color = "#2ecc71"  # สีเขียว
        self.danger_color = "#e74c3c"  # สีแดง
        self.warning_color = "#f39c12"  # สีส้ม
        self.bg_color = "#f5f5f5"  # สีพื้นหลัง
        self.dark_bg = "#2c3e50"  # สีพื้นหลังเข้ม

        # อนิเมชัน
        self.is_animating = False
        self.animation_thread = None

        # สร้าง UI components
        self.create_ui()

        # เริ่มอนิเมชัน
        self.start_animation()

    def create_ui(self):
        """สร้าง UI แบบ enhanced"""
        # สร้างสไตล์ปุ่ม
        style = ttk.Style()
        style.configure(
            "Primary.TButton", background=self.primary_color, foreground="black"
        )
        style.configure(
            "Success.TButton", background=self.success_color, foreground="black"
        )
        style.configure(
            "Danger.TButton", background=self.danger_color, foreground="black"
        )

        # กรอบหลัก
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill="both", expand=True)

        # ส่วนหัว - ทำให้โดดเด่น
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 10))

        title_frame = tk.Frame(header_frame, bg=self.primary_color)
        title_frame.pack(fill="x", padx=5, pady=5)

        title_label = tk.Label(
            title_frame,
            text="Fishing Assistent Bot",
            font=("Arial", 16, "bold"),
            fg="white",
            bg=self.primary_color,
        )
        title_label.pack(pady=10)

        # ข้อความแนะนำ
        tip_frame = ttk.Frame(main_frame)
        tip_frame.pack(fill="x", pady=5)

        tip_text = ttk.Label(
            tip_frame,
            text="Select region containing the fishing gauge and press Start",
            font=("Arial", 10, "italic"),
        )
        tip_text.pack(pady=5)

        # กรอบสถานะ - ปรับปรุงให้มีข้อมูลมากขึ้น
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding=10)
        status_frame.pack(fill="x", pady=10)

        # แยกเป็น 2 คอลัมน์
        status_columns = ttk.Frame(status_frame)
        status_columns.pack(fill="x")

        # คอลัมน์ซ้าย - สถานะ
        left_status = ttk.Frame(status_columns)
        left_status.pack(side="top", fill="x", expand=True)

        status_label_title = ttk.Label(
            left_status, text="Current Status:", font=("Arial", 10, "bold")
        )
        status_label_title.pack(side="left", padx=5)

        self.status_label = ttk.Label(left_status, text="Ready", font=("Arial", 10))
        self.status_label.pack(side="left", padx=5)

        # คอลัมน์ขวา - พื้นที่ (ให้ไปอยู่ใต้ Current Status)
        right_status = ttk.Frame(status_columns)
        right_status.pack(side="top", fill="x", expand=True)

        region_label_title = ttk.Label(
            right_status, text="Region:", font=("Arial", 10, "bold")
        )
        region_label_title.pack(side="left", padx=5)

        self.region_label = ttk.Label(
            right_status, text="No region selected", font=("Arial", 10)
        )
        self.region_label.pack(side="left", padx=5)

        # เพิ่มแถบความคืบหน้า
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(
            status_frame,
            orient="horizontal",
            length=200,
            mode="indeterminate",
            variable=self.progress_var,
        )
        self.progress.pack(fill="x", pady=(10, 0))

        # ปุ่มควบคุม - จัดให้สวยงาม
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding=10)
        control_frame.pack(fill="x", pady=10)

        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill="x", pady=5)

        # กำหนดคอลัมน์
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)

        # ปุ่มกด
        self.select_button = ttk.Button(
            button_frame,
            text="Select Region",
            command=self.app.select_gauge_region,
            style="Primary.TButton",
        )
        self.select_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.start_button = ttk.Button(
            button_frame,
            text="Start",
            command=self.app.start_fishing,
            state="disabled",
            style="Success.TButton",
        )
        self.start_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.stop_button = ttk.Button(
            button_frame,
            text="Stop",
            command=self.app.stop_fishing,
            state="disabled",
            style="Danger.TButton",
        )
        self.stop_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # เกจจำลอง - ปรับปรุงให้สวยงาม
        gauge_frame = ttk.LabelFrame(main_frame, text="Gauge Visualization", padding=10)
        gauge_frame.pack(fill="x", pady=10)

        self.gauge_canvas = tk.Canvas(
            gauge_frame, height=50, bg=self.dark_bg, highlightthickness=0
        )
        self.gauge_canvas.pack(fill="x", pady=5)

        # สร้างเกจจำลอง
        self.create_gauge()

        # ข้อมูลตัวชี้วัด
        indicator_frame = ttk.Frame(gauge_frame)
        indicator_frame.pack(fill="x")

        # แยกเป็น 2 คอลัมน์
        indicator_frame.columnconfigure(0, weight=1)
        indicator_frame.columnconfigure(1, weight=1)

        # ข้อมูลซ้าย - ตำแหน่ง
        left_info = ttk.Frame(indicator_frame)
        left_info.grid(row=0, column=0, sticky="w")

        position_label = ttk.Label(
            left_info, text="Position:", font=("Arial", 9, "bold")
        )
        position_label.pack(side="left", padx=2)

        self.position_value = ttk.Label(left_info, text="Center", font=("Arial", 9))
        self.position_value.pack(side="left", padx=2)

        # ข้อมูลขวา - โซน
        right_info = ttk.Frame(indicator_frame)
        right_info.grid(row=0, column=1, sticky="e")

        zone_label = ttk.Label(right_info, text="Zone:", font=("Arial", 9, "bold"))
        zone_label.pack(side="left", padx=2)

        self.zone_value = ttk.Label(right_info, text="Safe", font=("Arial", 9))
        self.zone_value.pack(side="left", padx=2)

        # Hotkey info
        footer_frame = ttk.Frame(main_frame)
        footer_frame.pack(fill="x", pady=(10, 0))

        hotkey_label = ttk.Label(
            footer_frame,
            text="Press 'F10' to stop at any time",
            foreground=self.danger_color,
            font=("Arial", 10, "bold"),
        )
        hotkey_label.pack(pady=5)

        # เวอร์ชั่น
        version_label = ttk.Label(
            footer_frame, text="v1.0", font=("Arial", 8), foreground="#7f8c8d"
        )
        version_label.pack(side="right", padx=5)

    def create_gauge(self):
        """สร้างเกจจำลองแบบสวยงาม"""
        # ความกว้างของ Canvas
        width = self.gauge_canvas.winfo_width()
        if width < 10:
            width = 380

        # ล้าง Canvas
        self.gauge_canvas.delete("all")

        # สร้างพื้นหลังแบบไล่ระดับ
        for i in range(20):
            y0 = i * 50 / 20
            y1 = (i + 1) * 50 / 20

            # สีไล่ระดับจากเข้มไปอ่อน
            intensity = 30 + int(20 * i / 20)
            color = f"#{intensity:02x}{intensity:02x}{intensity:02x}"

            self.gauge_canvas.create_rectangle(0, y0, width, y1, fill=color, outline="")

        # คำนวณขนาดโซน
        red_width = width * 0.2
        buffer_width = width * 0.05

        # สร้างโซนสีแดงซ้าย
        self.gauge_canvas.create_rectangle(
            0, 0, red_width, 50, fill=self.danger_color, outline="", stipple="gray25"
        )

        # สร้างโซนกันชนซ้าย (ไล่จากแดงเป็นเขียว)
        for i in range(10):
            x0 = red_width + i * buffer_width / 10
            x1 = red_width + (i + 1) * buffer_width / 10

            # ไล่สีจากแดงเป็นเขียว
            r = int(231 * (10 - i) / 10 + 46 * i / 10)
            g = int(76 * (10 - i) / 10 + 204 * i / 10)
            b = int(60 * (10 - i) / 10 + 113 * i / 10)

            color = f"#{r:02x}{g:02x}{b:02x}"

            self.gauge_canvas.create_rectangle(x0, 0, x1, 50, fill=color, outline="")

        # สร้างโซนสีเขียวกลาง
        self.gauge_canvas.create_rectangle(
            red_width + buffer_width,
            0,
            width - red_width - buffer_width,
            50,
            fill=self.success_color,
            outline="",
        )

        # สร้างโซนกันชนขวา (ไล่จากเขียวเป็นแดง)
        for i in range(10):
            x0 = width - red_width - buffer_width + i * buffer_width / 10
            x1 = width - red_width - buffer_width + (i + 1) * buffer_width / 10

            # ไล่สีจากเขียวเป็นแดง
            r = int(46 * (10 - i) / 10 + 231 * i / 10)
            g = int(204 * (10 - i) / 10 + 76 * i / 10)
            b = int(113 * (10 - i) / 10 + 60 * i / 10)

            color = f"#{r:02x}{g:02x}{b:02x}"

            self.gauge_canvas.create_rectangle(x0, 0, x1, 50, fill=color, outline="")

        # สร้างโซนสีแดงขวา
        self.gauge_canvas.create_rectangle(
            width - red_width,
            0,
            width,
            50,
            fill=self.danger_color,
            outline="",
            stipple="gray25",
        )

        # สร้างเส้นแบ่งโซน
        for x in [
            red_width,
            red_width + buffer_width,
            width - red_width - buffer_width,
            width - red_width,
        ]:
            self.gauge_canvas.create_line(
                x, 0, x, 50, fill="white", width=1, dash=(2, 4)
            )

        # สร้างเส้นกึ่งกลาง
        self.gauge_canvas.create_line(
            width / 2, 0, width / 2, 50, fill="white", width=1, dash=(1, 2)
        )

        # สร้างเส้นตัวชี้
        line_x = width / 2
        self.gauge_line = self.gauge_canvas.create_line(
            line_x, 0, line_x, 50, fill="white", width=2
        )

        # สร้างวงกลมที่ปลายเส้น
        self.gauge_circle = self.gauge_canvas.create_oval(
            line_x - 4, 0, line_x + 4, 8, fill="white", outline=""
        )

    def update_line_position(self, relative_pos):
        """อัปเดตตำแหน่งเส้นในเกจ"""
        width = self.gauge_canvas.winfo_width()
        if width < 10:
            width = 380

        line_x = width * relative_pos
        self.gauge_canvas.coords(self.gauge_line, line_x, 0, line_x, 50)
        self.gauge_canvas.coords(self.gauge_circle, line_x - 4, 0, line_x + 4, 8)

        # อัปเดตข้อมูลตำแหน่ง
        if relative_pos < 0.25:
            self.position_value.config(text="Left")
            self.zone_value.config(text="Warning", foreground=self.warning_color)
        elif relative_pos > 0.75:
            self.position_value.config(text="Right")
            self.zone_value.config(text="Danger", foreground=self.danger_color)
        else:
            self.position_value.config(text="Center")
            self.zone_value.config(text="Safe", foreground=self.success_color)

    def update_status(self, text, status_type="normal"):
        """อัปเดตข้อความสถานะ"""
        self.status_label.config(text=text)

        if status_type == "success":
            self.status_label.config(foreground=self.success_color)
            self.progress.stop()
            self.progress.config(mode="determinate")
            self.progress_var.set(100)
        elif status_type == "danger":
            self.status_label.config(foreground=self.danger_color)
            self.progress.stop()
            self.progress_var.set(0)
        elif status_type == "warning":
            self.status_label.config(foreground=self.warning_color)
            self.progress.config(mode="indeterminate")
            self.progress.start(15)
        else:
            self.status_label.config(foreground="black")
            self.progress.stop()
            self.progress_var.set(50)

    def update_region_info(self, region):
        """อัปเดตข้อมูลพื้นที่ที่เลือก"""
        if region:
            x1, y1, x2, y2 = region
            size = f"{x2-x1}x{y2-y1}"
            self.region_label.config(text=f"({x1}, {y1}) to ({x2}, {y2}) [{size}]")

            # แสดงการแจ้งเตือนข้อมูลการเลือกพื้นที่
            self.show_tooltip(f"Region selected: {size}")

    def set_start_button_state(self, state):
        """ตั้งค่าสถานะปุ่ม Start"""
        self.start_button.config(state=state)

    def set_button_states(self, select_state, start_state, stop_state):
        """ตั้งค่าสถานะของปุ่มทั้งหมด"""
        self.select_button.config(state=select_state)
        self.start_button.config(state=start_state)
        self.stop_button.config(state=stop_state)

    def start_animation(self):
        """เริ่มอนิเมชันเส้นตัวชี้"""
        self.is_animating = True
        self.animation_thread = threading.Thread(
            target=self._animation_loop, daemon=True
        )
        self.animation_thread.start()

    def stop_animation(self):
        """หยุดอนิเมชัน"""
        self.is_animating = False

    def _animation_loop(self):
        """ลูปอนิเมชันเส้นตัวชี้"""
        position = 0.5
        direction = 0.01

        while self.is_animating:
            # เคลื่อนเส้นเฉพาะเมื่อไม่ได้ทำงานจริง
            if not hasattr(self.app, "running") or not self.app.running:
                # เปลี่ยนทิศทางเมื่อถึงขอบ
                if position >= 0.95:
                    direction = -0.01
                elif position <= 0.05:
                    direction = 0.01

                # อัปเดตตำแหน่ง
                position += direction
                self.update_line_position(position)

            # หน่วงเวลา
            time.sleep(0.05)

    def show_tooltip(self, message, duration=2000):
        """แสดงทูลทิปแบบชั่วคราว"""
        # สร้างหน้าต่างทูลทิป
        tooltip = tk.Toplevel(self.root)
        tooltip.overrideredirect(True)
        tooltip.attributes("-topmost", True)

        # สร้างกรอบ
        frame = tk.Frame(tooltip, bg=self.primary_color, padx=10, pady=5)
        frame.pack()

        # สร้างข้อความ
        label = tk.Label(
            frame, text=message, bg=self.primary_color, fg="white", font=("Arial", 10)
        )
        label.pack()

        # จัดตำแหน่ง
        tooltip.update_idletasks()
        width = tooltip.winfo_reqwidth()
        height = tooltip.winfo_reqheight()

        x = self.root.winfo_rootx() + (self.root.winfo_width() - width) // 2
        y = self.root.winfo_rooty() + 50

        tooltip.geometry(f"+{x}+{y}")

        # ลบอัตโนมัติ
        tooltip.after(duration, tooltip.destroy)
