import tkinter as tk
import time
import threading


class GaugeVisualizer:
    def __init__(self, parent, theme_manager):
        self.parent = parent
        self.theme_manager = theme_manager

        # สร้าง Canvas สำหรับวาดเกจ
        self.canvas = tk.Canvas(parent, height=80, bg="#1f1f1f", highlightthickness=0)
        self.canvas.pack(fill="x", pady=10, padx=10)

        # ตัวแปรสำหรับตำแหน่งของเส้น
        self.line_position = 0.5  # Default position (middle)

        # สร้างเกจจำลอง
        self.create_gauge()

        # เริ่มอนิเมชัน
        self.animation_thread = threading.Thread(target=self.animate_gauge)
        self.animation_thread.daemon = True
        self.animation_thread.start()

    def create_gauge(self):
        """สร้างเกจจำลอง"""
        # ขนาด Canvas
        width = self.canvas.winfo_width()
        if width < 10:  # ถ้ายังไม่ได้แสดงผล
            width = 400  # ค่าเริ่มต้น

        # สร้างพื้นหลังเกจ
        self.gauge_bg = self.canvas.create_rectangle(
            20, 20, width - 20, 60, fill="#333333", outline=""
        )

        # สร้างโซนสีแดงซ้าย
        self.gauge_red_left = self.canvas.create_rectangle(
            20, 20, 100, 60, fill="#e74c3c", outline=""
        )

        # สร้างโซนสีเขียวกลาง
        self.gauge_green = self.canvas.create_rectangle(
            100, 20, width - 100, 60, fill="#2ecc71", outline=""
        )

        # สร้างโซนสีแดงขวา
        self.gauge_red_right = self.canvas.create_rectangle(
            width - 100, 20, width - 20, 60, fill="#e74c3c", outline=""
        )

        # สร้างเส้นตัวชี้
        line_x = width / 2
        self.gauge_line = self.canvas.create_line(
            line_x, 15, line_x, 65, fill="white", width=3
        )

        # ข้อความสถานะ
        self.status_text = self.canvas.create_text(
            width / 2, 70, text="Ready", fill="white", font=("Arial", 9)
        )

    def update_gauge_size(self):
        """อัปเดตขนาดเกจเมื่อขนาดหน้าต่างเปลี่ยนแปลง"""
        # ขนาด Canvas
        width = self.canvas.winfo_width()
        if width < 10:  # ถ้ายังไม่ได้แสดงผล
            return

        # อัปเดตตำแหน่งเกจ
        self.canvas.coords(self.gauge_bg, 20, 20, width - 20, 60)

        # คำนวณขนาดของแต่ละโซน
        zone_width = (width - 40) / 5

        # อัปเดตโซนสีแดงซ้าย
        self.canvas.coords(self.gauge_red_left, 20, 20, 20 + zone_width, 60)

        # อัปเดตโซนสีเขียวกลาง
        self.canvas.coords(
            self.gauge_green, 20 + zone_width, 20, width - 20 - zone_width, 60
        )

        # อัปเดตโซนสีแดงขวา
        self.canvas.coords(
            self.gauge_red_right, width - 20 - zone_width, 20, width - 20, 60
        )

        # อัปเดตตำแหน่งเส้นตัวชี้
        line_x = 20 + (width - 40) * self.line_position
        self.canvas.coords(self.gauge_line, line_x, 15, line_x, 65)

        # อัปเดตตำแหน่งข้อความสถานะ
        self.canvas.coords(self.status_text, width / 2, 70)

    def update_line_position(self, relative_pos):
        """อัปเดตตำแหน่งเส้นในเกจ"""
        self.line_position = max(0, min(1, relative_pos))  # จำกัดค่าระหว่าง 0-1

        # ขนาด Canvas
        width = self.canvas.winfo_width()
        if width < 10:  # ถ้ายังไม่ได้แสดงผล
            width = 400  # ค่าเริ่มต้น

        # คำนวณตำแหน่ง x
        line_x = 20 + (width - 40) * self.line_position

        # อัปเดตตำแหน่งเส้น
        self.canvas.coords(self.gauge_line, line_x, 15, line_x, 65)

    def update_status(self, text):
        """อัปเดตข้อความสถานะ"""
        self.canvas.itemconfig(self.status_text, text=text)

    def animate_gauge(self):
        """อนิเมชันของเกจ (สำหรับตอนแสดงตัวอย่าง)"""
        while True:
            # ตรวจสอบว่า Canvas ยังมีอยู่หรือไม่
            try:
                if not self.canvas.winfo_exists():
                    break

                # อัปเดตขนาดเกจ
                self.update_gauge_size()

                # หน่วงเวลา
                time.sleep(0.1)
            except Exception:
                break
