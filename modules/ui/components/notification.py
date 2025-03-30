import tkinter as tk
from tkinter import ttk
import time
import threading


class Notification:
    def __init__(
        self, root, message, notification_type="info", duration=3000, theme_manager=None
    ):
        self.root = root
        self.message = message
        self.notification_type = notification_type
        self.duration = duration
        self.theme_manager = theme_manager

        # สร้างหน้าต่างแจ้งเตือน
        self.create_notification()

    def create_notification(self):
        """สร้างหน้าต่างแจ้งเตือน"""
        # กำหนดสีตามประเภทการแจ้งเตือน
        color_map = {
            "info": "#3498db",  # สีน้ำเงิน
            "success": "#2ecc71",  # สีเขียว
            "warning": "#f39c12",  # สีส้ม
            "error": "#e74c3c",  # สีแดง
        }

        # สีพื้นหลัง
        bg_color = color_map.get(self.notification_type, "#3498db")

        # สร้างหน้าต่างแจ้งเตือน
        self.notification = tk.Toplevel(self.root)
        self.notification.overrideredirect(True)  # ไม่แสดงกรอบหน้าต่าง

        # ตั้งค่าตำแหน่ง
        # คำนวณขนาดและตำแหน่ง
        self.notification.withdraw()  # ซ่อนไว้ก่อนเพื่อคำนวณขนาด

        # สร้างเฟรมหลัก
        frame = tk.Frame(self.notification, bg=bg_color)
        frame.pack(fill="both", expand=True)

        # แสดงไอคอน
        icon_text = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}

        icon = tk.Label(
            frame,
            text=icon_text.get(self.notification_type, "ℹ️"),
            bg=bg_color,
            fg="white",
            font=("Arial", 16),
        )
        icon.pack(side="left", padx=10, pady=10)

        # แสดงข้อความ
        message = tk.Label(
            frame,
            text=self.message,
            bg=bg_color,
            fg="white",
            font=("Arial", 10),
            justify="left",
            wraplength=250,
        )
        message.pack(side="left", padx=5, pady=10)

        # ปุ่มปิด
        close_button = tk.Label(
            frame, text="×", bg=bg_color, fg="white", font=("Arial", 16), cursor="hand2"
        )
        close_button.pack(side="right", padx=10, pady=10)
        close_button.bind("<Button-1>", lambda e: self.close_notification())

        # ปรับขนาดและแสดงผล
        self.notification.update_idletasks()

        width = self.notification.winfo_reqwidth()
        height = self.notification.winfo_reqheight()

        # คำนวณตำแหน่ง (มุมขวาล่าง)
        x = self.root.winfo_rootx() + self.root.winfo_width() - width - 20
        y = self.root.winfo_rooty() + self.root.winfo_height() - height - 20

        # ตั้งค่าตำแหน่งและแสดงผล
        self.notification.geometry(f"{width}x{height}+{x}+{y}")
        self.notification.deiconify()

        # เริ่มนับเวลาปิดอัตโนมัติ
        self.after_id = self.root.after(self.duration, self.close_notification)

        # เอฟเฟกต์เฟด
        self.fade_in()

    def fade_in(self):
        """เอฟเฟกต์เฟดอิน"""
        for i in range(1, 11):
            alpha = i / 10
            self.notification.attributes("-alpha", alpha)
            self.notification.update()
            time.sleep(0.02)

    def fade_out(self):
        """เอฟเฟกต์เฟดเอาท์"""
        for i in range(10, 0, -1):
            alpha = i / 10
            self.notification.attributes("-alpha", alpha)
            self.notification.update()
            time.sleep(0.02)

    def close_notification(self):
        """ปิดการแจ้งเตือน"""
        try:
            # ยกเลิกการนับเวลา
            self.root.after_cancel(self.after_id)

            # เอฟเฟกต์เฟดเอาท์
            fade_thread = threading.Thread(target=self.fade_out)
            fade_thread.start()
            fade_thread.join()

            # ปิดหน้าต่าง
            self.notification.destroy()
        except Exception:
            # ในกรณีที่หน้าต่างถูกปิดไปแล้ว
            pass
