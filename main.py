import tkinter as tk
import keyboard
import os
import sys

# เพิ่มโฟลเดอร์ปัจจุบันในพาธ
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.pixelated_ui import PixelatedUI
from detector.gauge_detector import GaugeDetector
from utils.config_manager import (
    ConfigManager,
)  # เปลี่ยนจาก config.py เป็น utils.config_manager
from app_integration import integrate_settings  # เพิ่มการนำเข้าสำหรับการผสานหน้าตั้งค่า


class FishingBot:
    def __init__(self, root):
        self.root = root
        self.root.title("Fishing Assistant")
        self.root.geometry("430x780")
        self.root.resizable(False, False)

        # โหลดการตั้งค่า (จะถูกแทนที่ด้วย ConfigManager)
        # self.config = BotConfig()

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

        # ผสานหน้าตั้งค่าและโหลดค่าตั้งต้นจาก config.json
        self.config_manager, self.settings_ui, self.main_menu = integrate_settings(
            self, root
        )
        self.load_settings_from_config()

    def load_settings_from_config(self):
        """โหลดการตั้งค่าจาก config.json เข้าสู่แอพพลิเคชัน"""
        config = self.config_manager.config

        # ตั้งค่าพารามิเตอร์ต่างๆ
        self.line_threshold = config.get("line_threshold", 200)
        self.color_threshold = config.get("color_threshold", 30)
        self.action_cooldown = config.get("action_cooldown", 0.1)
        self.red_zone_threshold = config.get("red_zone_threshold", 0.2)
        self.buffer_zone_size = config.get("buffer_zone_size", 0.13)
        self.first_click_delay = config.get("first_click_delay", 1.0)
        self.periodic_click_interval = config.get("periodic_click_interval", 4.0)

        # อัปเดตค่าใน detector ถ้ามี
        if hasattr(self, "detector"):
            self.detector.line_threshold = self.line_threshold
            self.detector.color_threshold = self.color_threshold
            self.detector.action_cooldown = self.action_cooldown

        # อัปเดตสี UI ถ้าต้องการ
        ui_colors = config.get("ui_colors", {})
        if ui_colors and hasattr(self, "ui") and hasattr(self.ui, "gauge"):
            gauge_colors = {
                "success": ui_colors.get("success", "#2ecc71"),
                "danger": ui_colors.get("danger", "#e74c3c"),
                "warning": ui_colors.get("warning", "#f39c12"),
                "bg": self.ui.bg_color,
                "accent": self.ui.accent_color,
                "crt": self.ui.crt_color,
            }

            # อัปเดตสีของเกจ
            self.ui.gauge.set_gauge_color(
                success_color=gauge_colors["success"],
                danger_color=gauge_colors["danger"],
                warning_color=gauge_colors["warning"],
                accent_color=gauge_colors["accent"],
                crt_color=gauge_colors["crt"],
            )

    def select_gauge_region(self):
        """เรียกใช้ฟังก์ชันเลือกพื้นที่เกจ"""
        from detector.screen_selector import select_region

        region = select_region(self.root)
        if region:
            self.region = region
            self.ui.update_region_info(region)
            print(f"Region selected: {region}")
            self.ui.set_start_button_state("normal")
            self.ui.update_status("Region selected", "success")

    def start_fishing(self):
        """เริ่มการทำงานของบอท"""
        if not self.running and self.region:
            self.running = True
            self.ui.update_status("Starting...", "warning")

            # เริ่มการจับปลา
            import threading

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
