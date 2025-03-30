import tkinter as tk
from tkinter import ttk
import keyboard
import threading
import os
import json
from modules.ui.modern_ui import ModernUI
from modules.core.fishing_detector import FishingDetector
from modules.core.config_manager import ConfigManager
from modules.utils.hotkey_manager import HotkeyManager
from modules.utils.analytics import AnalyticsTracker


class FishingBotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fishing Master Pro")
        self.root.geometry("450x650")
        self.root.resizable(False, False)

        # ตั้งค่าไอคอนแอพ (ถ้ามี)
        try:
            icon_path = os.path.join("assets", "icons", "app_icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception:
            pass

        # โหลดการตั้งค่า
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()

        # สร้างระบบเก็บสถิติ
        self.analytics = AnalyticsTracker()

        # สถานะโปรแกรม
        self.running = False
        self.detection_thread = None

        # สร้าง UI เปล่าๆ ก่อน (ยังไม่มีการ build)
        self.ui = ModernUI(self)

        # สร้าง Detector
        self.detector = FishingDetector(self)

        # สร้าง Hotkey Manager
        self.hotkey_manager = HotkeyManager(self)

        # ตอนนี้ถึงให้ UI build อินเตอร์เฟซ
        self.ui.build_interface()

        # ตั้งค่าการปิดโปรแกรม
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def start_fishing(self):
        """เริ่มการทำงานของบอท"""
        if not self.running and self.detector.region:
            self.running = True
            self.ui.update_status("Starting...", "warning")

            # เริ่มการจับปลา
            self.detection_thread = threading.Thread(target=self.detector.fishing_loop)
            self.detection_thread.daemon = True
            self.detection_thread.start()

            # อัปเดต UI
            self.ui.set_button_states(select=False, start=False, stop=True)

            # เพิ่มจำนวนครั้งที่เริ่มทำงาน
            self.analytics.add_session_start()

    def stop_fishing(self):
        """หยุดการทำงานของบอท"""
        if self.running:
            self.running = False
            if self.detection_thread and self.detection_thread.is_alive():
                self.detection_thread.join(timeout=1.0)

            self.ui.update_status("Stopped", "inactive")
            self.ui.set_button_states(select=True, start=True, stop=False)

            # บันทึกสถิติเมื่อหยุด
            self.analytics.add_session_end()

    def save_settings(self):
        """บันทึกการตั้งค่าทั้งหมด"""
        # รวบรวมการตั้งค่าจาก UI
        settings = self.ui.get_all_settings()
        self.config.update(settings)

        # อัปเดตการตั้งค่าให้ detector
        self.detector.update_settings_from_config(self.config)

        # บันทึกลงไฟล์
        self.config_manager.save_config(self.config)

        self.ui.show_notification("Settings saved successfully", "success")

    def on_closing(self):
        """จัดการเมื่อปิดโปรแกรม"""
        # หยุดการทำงานทั้งหมด
        self.stop_fishing()

        # บันทึกการตั้งค่า
        self.save_settings()

        # ยกเลิกการลงทะเบียน hotkey
        self.hotkey_manager.unregister_all_hotkeys()

        # บันทึกสถิติการใช้งาน
        self.analytics.save_statistics()

        # ปิดโปรแกรม
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = FishingBotApp(root)
    root.mainloop()
