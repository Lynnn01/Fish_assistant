import tkinter as tk
from tkinter import ttk

from utils.constants import UI_CONSTANTS, PIXEL_COLORS


class MainMenu:
    """เมนูหลักของแอพพลิเคชันพร้อมตัวเลือกตั้งค่า"""

    def __init__(self, parent, settings_ui, config_manager, app=None):
        """
        สร้างเมนูหลักสำหรับแอพพลิเคชัน

        Args:
            parent: หน้าต่างหลักที่จะใช้เป็น parent
            settings_ui: อินสแตนซ์ของ SettingsUI
            config_manager: อินสแตนซ์ของ ConfigManager
            app: แอพพลิเคชันหลัก
        """
        self.parent = parent
        self.settings_ui = settings_ui
        self.config_manager = config_manager
        self.app = app

        # สร้างเมนูหลัก
        self.menu_bar = tk.Menu(parent)
        parent.config(menu=self.menu_bar)

        # เมนูไฟล์
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        self.file_menu.add_command(label="Settings", command=self.open_settings)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.parent.quit)

        # เมนูช่วยเหลือ
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)

        self.help_menu.add_command(label="About", command=self.show_about)
        self.help_menu.add_command(label="Hotkeys", command=self.show_hotkeys)

        # เพิ่มปุ่มตั้งค่าบนหน้าจอหลัก
        self.add_settings_button()

    def add_settings_button(self):
        """เพิ่มปุ่มตั้งค่าในหน้าจอหลัก"""
        # ถ้ามี footer_frame อยู่แล้ว ให้เพิ่มปุ่มตั้งค่าลงไป
        if hasattr(self.app, "ui") and hasattr(self.app.ui, "footer_frame"):
            settings_button = ttk.Button(
                self.app.ui.footer_frame,
                text="[ SETTINGS ]",
                command=self.open_settings,
                style="Pixel.TButton",
            )
            settings_button.pack(side="left", padx=5)

    def open_settings(self):
        """เปิดหน้าต่างตั้งค่า"""
        self.settings_ui.open_settings()

    def show_about(self):
        """แสดงหน้าต่างเกี่ยวกับโปรแกรม"""
        about_window = tk.Toplevel(self.parent)
        about_window.title("About")
        about_window.geometry("400x300")
        about_window.configure(bg=PIXEL_COLORS["BACKGROUND_DARK"])
        about_window.transient(self.parent)

        # สร้างเนื้อหา
        frame = ttk.Frame(about_window, style="Pixel.TFrame", padding=20)
        frame.pack(fill="both", expand=True)

        title = ttk.Label(
            frame,
            text="Fishing Assistant",
            style="PixelTitle.TLabel",
            font=(UI_CONSTANTS["FONT_FAMILY"], 16, "bold"),
        )
        title.pack(pady=10)

        version = ttk.Label(frame, text="Version 1.0", style="Pixel.TLabel")
        version.pack()

        desc = ttk.Label(
            frame,
            text="An automated fishing assistant with\n pixelated retro interface.",
            style="Pixel.TLabel",
            justify="center",
        )
        desc.pack(pady=10)

        copyright_text = ttk.Label(
            frame, text="© 2025 All Rights Reserved", style="Pixel.TLabel"
        )
        copyright_text.pack(pady=20)

        close_button = ttk.Button(
            frame, text="[ CLOSE ]", command=about_window.destroy, style="Pixel.TButton"
        )
        close_button.pack()

    def show_hotkeys(self):
        """แสดงคีย์ลัดของโปรแกรม"""
        hotkeys_window = tk.Toplevel(self.parent)
        hotkeys_window.title("Hotkeys")
        hotkeys_window.geometry("400x300")
        hotkeys_window.configure(bg=PIXEL_COLORS["BACKGROUND_DARK"])
        hotkeys_window.transient(self.parent)

        # สร้างเนื้อหา
        frame = ttk.Frame(hotkeys_window, style="Pixel.TFrame", padding=20)
        frame.pack(fill="both", expand=True)

        title = ttk.Label(
            frame,
            text="Keyboard Shortcuts",
            style="PixelTitle.TLabel",
            font=(UI_CONSTANTS["FONT_FAMILY"], 16, "bold"),
        )
        title.pack(pady=10)

        hotkeys_text = """
F10: Stop fishing
Ctrl+S: Open settings
Esc: Close current window
        """

        hotkeys = ttk.Label(
            frame, text=hotkeys_text, style="Pixel.TLabel", justify="left"
        )
        hotkeys.pack(pady=10)

        close_button = ttk.Button(
            frame,
            text="[ CLOSE ]",
            command=hotkeys_window.destroy,
            style="Pixel.TButton",
        )
        close_button.pack(pady=10)

        # เพิ่มคีย์ลัด Esc เพื่อปิดหน้าต่าง
        hotkeys_window.bind("<Escape>", lambda e: hotkeys_window.destroy())

        # เพิ่มคีย์ลัด Ctrl+S สำหรับเปิดการตั้งค่า
        self.parent.bind("<Control-s>", lambda e: self.open_settings())
