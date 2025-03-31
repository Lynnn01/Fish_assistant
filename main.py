import tkinter as tk
import threading
import keyboard
import os

from ui import PixelatedUI
from detector import GaugeDetector


class FishingBot:
    def __init__(self, root):
        self.root = root
        self.root.title("Fishing Master Bot")
        self.root.geometry("430x770")
        self.root.resizable(False, False)

        # สถานะโปรแกรม
        self.running = False
        self.region = None
        self.detection_thread = None

        # สร้าง UI
        self.ui = PixelatedUI(root, self)

        # สร้างตัวตรวจจับ
        self.detector = GaugeDetector(self)

        # ลงทะเบียน Hotkey
        keyboard.add_hotkey("f10", self.stop_fishing)

        # ตั้งค่าการปิดโปรแกรม
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def select_gauge_region(self):
        """เรียกใช้ฟังก์ชันเลือกพื้นที่เกจ"""
        region = self.detector.select_region(self.root)
        if region:
            self.region = region
            self.ui.update_region_info(region)
            self.ui.set_start_button_state("normal")
            self.ui.update_status("Region selected", "success")

    def start_fishing(self):
        """เริ่มการทำงานของบอท"""
        if not self.running and self.region:
            self.running = True
            self.ui.update_status("Starting...", "warning")

            # เริ่มการจับปลา
            self.detection_thread = threading.Thread(target=self.fishing_loop)
            self.detection_thread.daemon = True
            self.detection_thread.start()

            # อัปเดต UI
            self.ui.set_button_states("disabled", "disabled", "normal")

    def stop_fishing(self):
        """หยุดการทำงานของบอท"""
        self.running = False
        if self.detection_thread and self.detection_thread.is_alive():
            self.detection_thread.join(timeout=1.0)

        self.ui.update_status("Stopped", "danger")
        self.ui.set_button_states("normal", "normal", "disabled")

    def fishing_loop(self):
        """ลูปหลักสำหรับการตกปลา"""
        self.detector.fishing_loop(self.region, self.ui)

    def on_closing(self):
        """จัดการเมื่อปิดโปรแกรม"""
        self.stop_fishing()
        self.ui.stop_animation()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = FishingBot(root)
    root.mainloop()
