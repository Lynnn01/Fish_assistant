import tkinter as tk
from tkinter import ttk
import sys
import os

# เพิ่มไดเร็กทอรีปัจจุบันในพาธเพื่อให้สามารถนำเข้าโมดูลได้
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.settings_ui import SettingsUI
from ui.main_menu import MainMenu
from utils.config_manager import ConfigManager
from ui.styles import apply_styles
from ui.settings_styles import apply_settings_styles
from utils.constants import UI_CONSTANTS, PIXEL_COLORS


class SettingsApp:
    """แอพพลิเคชันสำหรับทดสอบหน้าตั้งค่า"""

    def __init__(self, root):
        """
        สร้างแอพพลิเคชันสำหรับทดสอบหน้าตั้งค่า

        Args:
            root: หน้าต่างหลัก
        """
        self.root = root
        self.root.title("Fishing Assistant - Settings Test")
        self.root.geometry(
            f"{UI_CONSTANTS['WINDOW_WIDTH']}x{UI_CONSTANTS['WINDOW_HEIGHT']}"
        )
        self.root.configure(bg=PIXEL_COLORS["BACKGROUND_DARK"])

        # สร้าง style
        self.style = ttk.Style()
        apply_styles(self.style)
        apply_settings_styles(self.style)

        # สร้างตัวจัดการการตั้งค่า
        self.config_manager = ConfigManager("config.json")
        self.config_manager.register_observer(self.on_config_changed)

        # สร้างหน้าตั้งค่า
        self.settings_ui = SettingsUI(self.root, "config.json")

        # สร้างเมนูหลัก
        self.main_menu = MainMenu(
            self.root, self.settings_ui, self.config_manager, self
        )

        # สร้างหน้าตาเริ่มต้น
        self.create_main_interface()

        # เพิ่มคีย์ลัด
        self.setup_hotkeys()

    def create_main_interface(self):
        """สร้างอินเตอร์เฟซหลักอย่างง่าย"""
        # สร้างเฟรมหลัก
        main_frame = ttk.Frame(
            self.root, style="Pixel.TFrame", padding=UI_CONSTANTS["PADDING"]
        )
        main_frame.pack(fill="both", expand=True)

        # ส่วนหัว
        header_frame = ttk.Frame(main_frame, style="PixelPanel.TFrame")
        header_frame.pack(fill="x", pady=(0, 15), ipady=5)

        title_label = tk.Label(
            header_frame,
            text="╔═════════════════════════╗\n"
            "║    FISHING ASSISTANT    ║\n"
            "╚═════════════════════════╝",
            font=(UI_CONSTANTS["FONT_FAMILY"], 14, "bold"),
            fg=PIXEL_COLORS["TEXT_LIGHT"],
            bg=PIXEL_COLORS["PANEL_BG"],
            justify="center",
        )
        title_label.pack(pady=(5, 5))

        # ส่วนเนื้อหา
        content_frame = ttk.LabelFrame(
            main_frame, text="MAIN PANEL", style="Pixel.TLabelframe", padding=10
        )
        content_frame.pack(fill="both", expand=True, pady=10)

        # ข้อความแนะนำ
        prompt_label = ttk.Label(
            content_frame,
            text="Use the Settings menu or button below to open settings window.",
            style="Pixel.TLabel",
            wraplength=350,
        )
        prompt_label.pack(pady=20)

        # ปุ่มเปิดการตั้งค่า
        settings_button = ttk.Button(
            content_frame,
            text="[ OPEN SETTINGS ]",
            command=self.settings_ui.open_settings,
            style="PixelSuccess.TButton",
        )
        settings_button.pack(pady=10)

        # ส่วนท้าย
        self.footer_frame = ttk.Frame(main_frame, style="Pixel.TFrame")
        self.footer_frame.pack(fill="x", pady=(10, 0), side="bottom")

        # เวอร์ชัน
        version_label = tk.Label(
            self.footer_frame,
            text="[v1.0]",
            fg=PIXEL_COLORS["ACCENT_BLUE"],
            bg=PIXEL_COLORS["BACKGROUND_DARK"],
            font=(UI_CONSTANTS["FONT_FAMILY"], 8),
        )
        version_label.pack(side="right", padx=5)

        # เพิ่มปุ่มตั้งค่า
        self.main_menu.add_settings_button()

    def setup_hotkeys(self):
        """ตั้งค่าคีย์ลัดต่างๆ"""
        # Ctrl+S เพื่อเปิดการตั้งค่า
        self.root.bind("<Control-s>", lambda e: self.settings_ui.open_settings())

        # Esc เพื่อปิดโปรแกรม (ในโหมดทดสอบ)
        self.root.bind("<Escape>", lambda e: self.root.destroy())

    def on_config_changed(self, config):
        """จัดการเมื่อการตั้งค่าเปลี่ยนแปลง"""
        print("การตั้งค่าถูกเปลี่ยนแปลง:", config)

        # ในแอพจริง คุณอาจจะอัปเดต UI หรือฟังก์ชันการทำงานตามการตั้งค่าใหม่ที่นี่
        # เช่น อัปเดตสีของ UI, อัปเดตค่าต่างๆ ฯลฯ


if __name__ == "__main__":
    root = tk.Tk()
    app = SettingsApp(root)
    root.mainloop()
