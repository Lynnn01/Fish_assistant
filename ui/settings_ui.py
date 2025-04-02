import tkinter as tk
from tkinter import ttk
import json
import os

from ui.settings_components import ThresholdSettings, ColorSettings, TimingSettings
from utils.constants import UI_CONSTANTS, PIXEL_COLORS, DEFAULT_CONFIG


class SettingsUI:
    """หน้าตั้งค่าหลักสำหรับแอพพลิเคชัน"""

    def __init__(self, parent, config_file="config.json"):
        """
        สร้างหน้าตั้งค่าที่สามารถปรับได้จริง

        Args:
            parent: หน้าต่างหลักที่จะใช้เป็น parent
            config_file: ที่อยู่ของไฟล์ config.json
        """
        self.parent = parent
        self.config_file = config_file
        self.settings_window = None

        # โหลดการตั้งค่าปัจจุบัน
        self.config = self.load_config()

        # ตัวแปรเก็บข้อมูลสี
        self.colors = {
            "bg": PIXEL_COLORS["BACKGROUND_DARK"],
            "text": PIXEL_COLORS["TEXT_LIGHT"],
            "panel_bg": PIXEL_COLORS["PANEL_BG"],
            "primary": PIXEL_COLORS["PRIMARY_BLUE"],
            "success": PIXEL_COLORS["SUCCESS_GREEN"],
            "danger": PIXEL_COLORS["DANGER_RED"],
            "warning": PIXEL_COLORS["WARNING_YELLOW"],
            "accent": PIXEL_COLORS["ACCENT_BLUE"],
            "crt": PIXEL_COLORS["TEXT_LIGHT"],
        }

    def load_config(self):
        """โหลดการตั้งค่าจากไฟล์ config.json"""
        try:
            with open(self.config_file, "r") as f:
                config = json.load(f)
                # ตรวจสอบและเพิ่มค่าที่ขาดหายไป
                self._verify_and_update_config(config)
                return config
        except (FileNotFoundError, json.JSONDecodeError):
            # ถ้าไฟล์ไม่มีหรือมีปัญหา ใช้ค่าเริ่มต้น
            return DEFAULT_CONFIG.copy()

    def _verify_and_update_config(self, config):
        """ตรวจสอบว่ามีค่าที่จำเป็นทั้งหมดหรือไม่ ถ้าไม่มีให้เพิ่มจากค่า default"""
        updated = False

        # ตรวจสอบค่าหลัก
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value
                updated = True
            elif key == "ui_colors" and isinstance(value, dict):
                # ตรวจสอบค่าสีย่อย
                if not isinstance(config[key], dict):
                    config[key] = value
                    updated = True
                else:
                    for color_key, color_value in value.items():
                        if color_key not in config[key]:
                            config[key][color_key] = color_value
                            updated = True

        # บันทึกการเปลี่ยนแปลงถ้ามีการอัปเดต
        if updated:
            self.save_config(config)

        return config

    def save_config(self, config=None):
        """บันทึกการตั้งค่าลงไฟล์ config.json

        Args:
            config: ข้อมูลการตั้งค่าที่จะบันทึก (หากไม่ระบุจะใช้ค่าปัจจุบัน)
        """
        if config is None:
            config = self.config

        try:
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=4)
            return True
        except Exception as e:
            print(f"ไม่สามารถบันทึก config ได้: {e}")
            return False

    def open_settings(self):
        """เปิดหน้าต่างตั้งค่า"""
        # ถ้ามีหน้าต่างอยู่แล้ว ให้นำกลับมาแสดง
        if self.settings_window and self.settings_window.winfo_exists():
            self.settings_window.focus_force()
            return

        # สร้างหน้าต่างใหม่
        self.settings_window = tk.Toplevel(self.parent)
        self.settings_window.title("Fishing Assistant - Settings")

        try:
            self.settings_window.iconbitmap("assets/fish.ico")
        except:
            pass

        # ตั้งค่าหน้าต่าง
        self.settings_window.configure(bg=self.colors["bg"])
        self.settings_window.geometry("480x820")
        self.settings_window.resizable(False, False)
        self.settings_window.transient(self.parent)  # ทำให้เป็นหน้าต่างย่อยของหน้าต่างหลัก

        # กรอบหลัก
        main_frame = ttk.Frame(self.settings_window, style="Pixel.TFrame", padding=10)
        main_frame.pack(fill="both", expand=True)

        # ส่วนหัว
        header_frame = ttk.Frame(main_frame, style="PixelPanel.TFrame")
        header_frame.pack(fill="x", pady=(0, 10), ipady=5)

        title_label = tk.Label(
            header_frame,
            text="╔═══════════════════════╗\n"
            "║     SETTINGS MENU     ║\n"
            "╚═══════════════════════╝",
            font=(UI_CONSTANTS["FONT_FAMILY"], 14, "bold"),
            fg=self.colors["crt"],
            bg=self.colors["panel_bg"],
            justify="center",
        )
        title_label.pack(pady=(5, 5))

        # สร้าง notebook (แท็บ)
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True, pady=10)

        # สร้างแท็บ
        threshold_tab = ttk.Frame(notebook, style="Pixel.TFrame")
        color_tab = ttk.Frame(notebook, style="Pixel.TFrame")
        timing_tab = ttk.Frame(notebook, style="Pixel.TFrame")

        notebook.add(threshold_tab, text=" Thresholds ")
        notebook.add(color_tab, text=" Colors ")
        notebook.add(timing_tab, text=" Timing ")

        # สร้างส่วนประกอบแต่ละแท็บ
        self.threshold_settings = ThresholdSettings(threshold_tab, self.config)
        self.color_settings = ColorSettings(color_tab, self.config)
        self.timing_settings = TimingSettings(timing_tab, self.config)

        # ปุ่มควบคุม
        control_frame = ttk.Frame(main_frame, style="Pixel.TFrame")
        control_frame.pack(fill="x", pady=10)

        # แบ่งปุ่มเป็น 3 คอลัมน์
        control_frame.columnconfigure(0, weight=1)
        control_frame.columnconfigure(1, weight=1)
        control_frame.columnconfigure(2, weight=1)

        # ปุ่มรีเซ็ต
        reset_button = ttk.Button(
            control_frame,
            text="[ RESET DEFAULTS ]",
            command=self.reset_defaults,
            style="PixelDanger.TButton",
        )
        reset_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # ปุ่มบันทึก
        save_button = ttk.Button(
            control_frame,
            text="[ SAVE SETTINGS ]",
            command=self.save_settings,
            style="PixelSuccess.TButton",
        )
        save_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # ปุ่มยกเลิก
        cancel_button = ttk.Button(
            control_frame,
            text="[ CANCEL ]",
            command=self.settings_window.destroy,
            style="Pixel.TButton",
        )
        cancel_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # ส่วนล่าง
        footer_frame = ttk.Frame(main_frame, style="Pixel.TFrame")
        footer_frame.pack(fill="x", pady=(5, 0))

        note_label = tk.Label(
            footer_frame,
            text="Note: Changes will take effect after saving.",
            fg=self.colors["warning"],
            bg=self.colors["bg"],
            font=(UI_CONSTANTS["FONT_FAMILY"], 9),
        )
        note_label.pack(side="left", padx=5)

    def save_settings(self):
        """บันทึกการตั้งค่าจากแต่ละแท็บ"""
        # รวบรวมการตั้งค่าจากทุกส่วน
        threshold_config = self.threshold_settings.get_settings()
        color_config = self.color_settings.get_settings()
        timing_config = self.timing_settings.get_settings()

        # อัปเดต config
        self.config.update(threshold_config)
        self.config.update(color_config)
        self.config.update(timing_config)

        # บันทึกลงไฟล์
        if self.save_config(self.config):
            # แสดงการบันทึกสำเร็จ
            self._show_success_message("Settings saved successfully!")
            # ปิดหน้าต่าง
            self.settings_window.after(1500, self.settings_window.destroy)
        else:
            # แสดงข้อความเตือนเมื่อบันทึกไม่สำเร็จ
            self._show_error_message("Failed to save settings!")

    def reset_defaults(self):
        """รีเซ็ตการตั้งค่าเป็นค่าเริ่มต้น"""
        # ใช้ค่า default จาก constants
        default_config = DEFAULT_CONFIG.copy()

        # อัปเดตส่วนต่างๆ ด้วยค่าเริ่มต้น
        self.threshold_settings.update_settings(default_config)
        self.color_settings.update_settings(default_config)
        self.timing_settings.update_settings(default_config)

        # แสดงข้อความการรีเซ็ต
        self._show_success_message("Reset to default settings!")

    def _show_success_message(self, message):
        """แสดงข้อความแจ้งเตือนสำเร็จ"""
        msg_window = tk.Toplevel(self.settings_window)
        msg_window.overrideredirect(True)
        msg_window.configure(bg=self.colors["bg"])
        msg_window.attributes("-topmost", True)

        # สร้างกรอบข้อความ
        msg_frame = tk.Frame(
            msg_window,
            bg=self.colors["bg"],
            highlightbackground=self.colors["success"],
            highlightthickness=2,
            padx=20,
            pady=10,
        )
        msg_frame.pack()

        # ข้อความ
        msg_label = tk.Label(
            msg_frame,
            text=message,
            fg=self.colors["success"],
            bg=self.colors["bg"],
            font=(UI_CONSTANTS["FONT_FAMILY"], 12, "bold"),
        )
        msg_label.pack(pady=10)

        # จัดตำแหน่ง
        msg_window.update_idletasks()
        width = msg_window.winfo_reqwidth()
        height = msg_window.winfo_reqheight()

        parent_x = self.settings_window.winfo_rootx()
        parent_y = self.settings_window.winfo_rooty()
        parent_width = self.settings_window.winfo_width()
        parent_height = self.settings_window.winfo_height()

        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2

        msg_window.geometry(f"+{x}+{y}")

        # ปิดหลังจาก 1.5 วินาที
        msg_window.after(1500, msg_window.destroy)

    def _show_error_message(self, message):
        """แสดงข้อความแจ้งเตือนผิดพลาด"""
        msg_window = tk.Toplevel(self.settings_window)
        msg_window.overrideredirect(True)
        msg_window.configure(bg=self.colors["bg"])
        msg_window.attributes("-topmost", True)

        # สร้างกรอบข้อความ
        msg_frame = tk.Frame(
            msg_window,
            bg=self.colors["bg"],
            highlightbackground=self.colors["danger"],
            highlightthickness=2,
            padx=20,
            pady=10,
        )
        msg_frame.pack()

        # ข้อความ
        msg_label = tk.Label(
            msg_frame,
            text=message,
            fg=self.colors["danger"],
            bg=self.colors["bg"],
            font=(UI_CONSTANTS["FONT_FAMILY"], 12, "bold"),
        )
        msg_label.pack(pady=10)

        # จัดตำแหน่ง
        msg_window.update_idletasks()
        width = msg_window.winfo_reqwidth()
        height = msg_window.winfo_reqheight()

        parent_x = self.settings_window.winfo_rootx()
        parent_y = self.settings_window.winfo_rooty()
        parent_width = self.settings_window.winfo_width()
        parent_height = self.settings_window.winfo_height()

        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2

        msg_window.geometry(f"+{x}+{y}")

        # ปิดหลังจาก 1.5 วินาที
        msg_window.after(1500, msg_window.destroy)
