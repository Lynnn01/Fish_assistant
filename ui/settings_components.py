import tkinter as tk
from tkinter import ttk, colorchooser
import re
from functools import partial

from utils.constants import UI_CONSTANTS, PIXEL_COLORS


class PixelSlider:
    """สไลเดอร์แบบพิกเซลอาร์ตพร้อมค่าตัวเลข"""

    def __init__(
        self,
        parent,
        label,
        min_val,
        max_val,
        current_val,
        decimal_places=2,
        command=None,
        width=350,
    ):
        """
        สร้างสไลเดอร์แบบพิกเซลอาร์ตที่มีช่องแสดงค่าตัวเลข

        Args:
            parent: Widget ที่จะเป็น parent
            label: ข้อความแสดงรายละเอียดของสไลเดอร์
            min_val: ค่าต่ำสุด
            max_val: ค่าสูงสุด
            current_val: ค่าปัจจุบัน
            decimal_places: จำนวนตำแหน่งทศนิยม
            command: ฟังก์ชันที่จะเรียกเมื่อค่าเปลี่ยน
            width: ความกว้างของสไลเดอร์
        """
        self.parent = parent
        self.min_val = min_val
        self.max_val = max_val
        self.decimal_places = decimal_places
        self.command = command

        # สร้างเฟรมหลัก
        self.frame = ttk.Frame(parent, style="Pixel.TFrame")
        self.frame.pack(fill="x", pady=5)

        # ป้ายกำกับ
        self.label_frame = ttk.Frame(self.frame, style="Pixel.TFrame")
        self.label_frame.pack(fill="x")

        self.label = ttk.Label(self.label_frame, text=label, style="Pixel.TLabel")
        self.label.pack(side="left", pady=2)

        # ส่วนแสดงค่าตัวเลข
        self.value_var = tk.StringVar()
        self.value_entry = ttk.Entry(
            self.label_frame,
            textvariable=self.value_var,
            width=8,
            justify="center",
            style="Pixel.TEntry",
        )
        self.value_entry.pack(side="right", padx=5)

        # สร้างสไลเดอร์
        self.slider_frame = ttk.Frame(self.frame, style="Pixel.TFrame")
        self.slider_frame.pack(fill="x", pady=2)

        # ป้ายแสดงค่าต่ำสุด
        self.min_label = ttk.Label(
            self.slider_frame,
            text=f"{min_val:.{decimal_places}f}",
            style="Pixel.TLabel",
        )
        self.min_label.pack(side="left", padx=5)

        # สไลเดอร์
        self.slider = ttk.Scale(
            self.slider_frame,
            from_=min_val,
            to=max_val,
            orient="horizontal",
            length=width,
            command=self._on_slider_change,
            style="Pixel.Horizontal.TScale",
        )
        self.slider.pack(side="left", fill="x", expand=True, padx=5)

        # ป้ายแสดงค่าสูงสุด
        self.max_label = ttk.Label(
            self.slider_frame,
            text=f"{max_val:.{decimal_places}f}",
            style="Pixel.TLabel",
        )
        self.max_label.pack(side="right", padx=5)

        # เส้นคั่น
        separator = ttk.Separator(self.frame, orient="horizontal")
        separator.pack(fill="x", pady=5)

        # ตั้งค่าเริ่มต้น
        self.set_value(current_val)

        # ผูกเหตุการณ์กับช่องป้อนค่า
        self.value_entry.bind("<Return>", self._on_entry_change)
        self.value_entry.bind("<FocusOut>", self._on_entry_change)

    def _on_slider_change(self, event):
        """จัดการเมื่อสไลเดอร์เปลี่ยนค่า"""
        value = self.slider.get()
        formatted_value = f"{value:.{self.decimal_places}f}"
        self.value_var.set(formatted_value)

        if self.command:
            self.command(value)

    def _on_entry_change(self, event):
        """จัดการเมื่อมีการป้อนค่าในช่องข้อความ"""
        try:
            value = float(self.value_var.get())
            # จำกัดค่าให้อยู่ในช่วงที่กำหนด
            value = max(self.min_val, min(self.max_val, value))

            # อัปเดตค่าในสไลเดอร์
            self.slider.set(value)

            # อัปเดตค่าในช่องข้อความให้มีรูปแบบที่ถูกต้อง
            formatted_value = f"{value:.{self.decimal_places}f}"
            self.value_var.set(formatted_value)

            if self.command:
                self.command(value)
        except ValueError:
            # ถ้าค่าไม่ถูกต้อง ให้ใช้ค่าปัจจุบันของสไลเดอร์
            current_value = self.slider.get()
            formatted_value = f"{current_value:.{self.decimal_places}f}"
            self.value_var.set(formatted_value)

    def get_value(self):
        """คืนค่าปัจจุบันของสไลเดอร์"""
        return self.slider.get()

    def set_value(self, value):
        """ตั้งค่าสไลเดอร์"""
        value = max(self.min_val, min(self.max_val, value))
        self.slider.set(value)
        formatted_value = f"{value:.{self.decimal_places}f}"
        self.value_var.set(formatted_value)


class PixelColorPicker:
    """ตัวเลือกสีแบบพิกเซลอาร์ต"""

    def __init__(self, parent, label, current_color, command=None):
        """
        สร้างตัวเลือกสีแบบพิกเซลอาร์ต

        Args:
            parent: Widget ที่จะเป็น parent
            label: ข้อความกำกับช่องสี
            current_color: สีปัจจุบัน (รหัสสี HEX, เช่น "#FF0000")
            command: ฟังก์ชันที่จะเรียกเมื่อสีเปลี่ยน
        """
        self.parent = parent
        self.current_color = current_color
        self.command = command

        # สร้างเฟรมหลัก
        self.frame = ttk.Frame(parent, style="Pixel.TFrame")
        self.frame.pack(fill="x", pady=5)

        # ป้ายกำกับ
        self.label = ttk.Label(self.frame, text=label, style="Pixel.TLabel")
        self.label.pack(side="left", pady=2)

        # ส่วนแสดงสีปัจจุบัน
        self.color_display = tk.Canvas(
            self.frame,
            width=30,
            height=20,
            highlightthickness=1,
            highlightbackground=PIXEL_COLORS["PANEL_BG"],
        )
        self.color_display.pack(side="right", padx=5)

        # ปุ่มเลือกสี
        self.color_button = ttk.Button(
            self.frame,
            text="Choose Color",
            command=self.choose_color,
            style="Pixel.TButton",
            width=15,
        )
        self.color_button.pack(side="right", padx=5)

        # ช่องแสดงค่าสี
        self.color_var = tk.StringVar(value=current_color)
        self.color_entry = ttk.Entry(
            self.frame,
            textvariable=self.color_var,
            width=8,
            justify="center",
            style="Pixel.TEntry",
        )
        self.color_entry.pack(side="right", padx=5)

        # อัปเดตสีเริ่มต้น
        self.update_color_display(current_color)

        # ผูกเหตุการณ์กับช่องป้อนค่า
        self.color_entry.bind("<Return>", self.validate_color)
        self.color_entry.bind("<FocusOut>", self.validate_color)

    def choose_color(self):
        """เปิดหน้าต่างเลือกสี"""
        color = colorchooser.askcolor(initialcolor=self.current_color)
        if color[1]:  # ถ้ามีการเลือกสี
            self.update_color(color[1])

    def update_color(self, color):
        """อัปเดตสีทั้งหมด"""
        self.current_color = color
        self.color_var.set(color)
        self.update_color_display(color)

        if self.command:
            self.command(color)

    def update_color_display(self, color):
        """อัปเดตช่องแสดงสี"""
        try:
            self.color_display.config(bg=color)
        except tk.TclError:
            # ถ้าสีไม่ถูกต้อง ใช้สีเริ่มต้น
            self.color_display.config(bg="#000000")

    def validate_color(self, event):
        """ตรวจสอบรูปแบบสีที่ป้อน"""
        color = self.color_var.get()

        # ตรวจสอบรูปแบบสี HEX
        if re.match(r"^#[0-9A-Fa-f]{6}$", color):
            self.update_color(color)
        else:
            # ถ้ารูปแบบไม่ถูกต้อง ใช้ค่าเดิม
            self.color_var.set(self.current_color)

    def get_color(self):
        """คืนค่าสีปัจจุบัน"""
        return self.current_color


class ThresholdSettings:
    """ส่วนการตั้งค่าเกณฑ์ต่างๆ"""

    def __init__(self, parent, config):
        """
        สร้างส่วนตั้งค่าเกณฑ์

        Args:
            parent: Widget ที่จะเป็น parent
            config: ข้อมูลการตั้งค่าปัจจุบัน
        """
        self.parent = parent
        self.config = config

        # สร้างเฟรมหลัก
        self.main_frame = ttk.Frame(parent, style="Pixel.TFrame", padding=10)
        self.main_frame.pack(fill="both", expand=True)

        # หัวข้อ
        title_label = ttk.Label(
            self.main_frame,
            text="Gauge & Detection Thresholds",
            style="PixelTitle.TLabel",
        )
        title_label.pack(pady=(0, 10))

        # คำอธิบาย
        desc_label = ttk.Label(
            self.main_frame,
            text="Adjust thresholds for gauge zones and detection sensitivity.",
            style="Pixel.TLabel",
            wraplength=400,
        )
        desc_label.pack(pady=(0, 10))

        # กรอบการตั้งค่าโซน
        zone_frame = ttk.LabelFrame(
            self.main_frame, text="Gauge Zones", style="Pixel.TLabelframe", padding=10
        )
        zone_frame.pack(fill="x", pady=5)

        # สไลเดอร์สำหรับโซนแดง
        self.red_zone_slider = PixelSlider(
            zone_frame,
            "Red Zone Width:",
            0.1,
            0.4,
            self.config.get("red_zone_threshold", 0.2),
            decimal_places=2,
        )

        # สไลเดอร์สำหรับโซนบัฟเฟอร์
        self.buffer_zone_slider = PixelSlider(
            zone_frame,
            "Buffer Zone Width:",
            0.05,
            0.2,
            self.config.get("buffer_zone_size", 0.13),
            decimal_places=2,
        )

        # กรอบการตั้งค่าการตรวจจับ
        detection_frame = ttk.LabelFrame(
            self.main_frame,
            text="Detection Sensitivity",
            style="Pixel.TLabelframe",
            padding=10,
        )
        detection_frame.pack(fill="x", pady=5)

        # สไลเดอร์สำหรับค่าเกณฑ์เส้น
        self.line_threshold_slider = PixelSlider(
            detection_frame,
            "Line Threshold:",
            100,
            255,
            self.config.get("line_threshold", 200),
            decimal_places=0,
        )

        # สไลเดอร์สำหรับค่าเกณฑ์สี
        self.color_threshold_slider = PixelSlider(
            detection_frame,
            "Color Threshold:",
            10,
            100,
            self.config.get("color_threshold", 30),
            decimal_places=0,
        )

        # คำแนะนำ
        tip_frame = ttk.Frame(self.main_frame, style="Pixel.TFrame")
        tip_frame.pack(fill="x", pady=10)

        tip_label = ttk.Label(
            tip_frame,
            text="TIP: Higher line threshold = less sensitive to movement\nHigher color threshold = less sensitive to color changes",
            style="PixelWarning.TLabel",
            justify="left",
        )
        tip_label.pack(anchor="w")

    def get_settings(self):
        """รับค่าการตั้งค่าปัจจุบัน"""
        return {
            "red_zone_threshold": self.red_zone_slider.get_value(),
            "buffer_zone_size": self.buffer_zone_slider.get_value(),
            "line_threshold": int(self.line_threshold_slider.get_value()),
            "color_threshold": int(self.color_threshold_slider.get_value()),
        }

    def update_settings(self, config):
        """อัปเดตการตั้งค่าจาก config"""
        self.red_zone_slider.set_value(config.get("red_zone_threshold", 0.2))
        self.buffer_zone_slider.set_value(config.get("buffer_zone_size", 0.13))
        self.line_threshold_slider.set_value(config.get("line_threshold", 200))
        self.color_threshold_slider.set_value(config.get("color_threshold", 30))


class ColorSettings:
    """ส่วนการตั้งค่าสี"""

    def __init__(self, parent, config):
        """
        สร้างส่วนตั้งค่าสี

        Args:
            parent: Widget ที่จะเป็น parent
            config: ข้อมูลการตั้งค่าปัจจุบัน
        """
        self.parent = parent
        self.config = config
        self.color_pickers = {}

        # ดึงการตั้งค่าสีปัจจุบัน
        self.ui_colors = self.config.get(
            "ui_colors",
            {
                "primary": "#3498db",
                "success": "#2ecc71",
                "danger": "#e74c3c",
                "warning": "#f39c12",
                "background": "#f5f5f5",
            },
        )

        # สร้างเฟรมหลัก
        self.main_frame = ttk.Frame(parent, style="Pixel.TFrame", padding=10)
        self.main_frame.pack(fill="both", expand=True)

        # หัวข้อ
        title_label = ttk.Label(
            self.main_frame, text="UI Color Settings", style="PixelTitle.TLabel"
        )
        title_label.pack(pady=(0, 10))

        # คำอธิบาย
        desc_label = ttk.Label(
            self.main_frame,
            text="Customize the appearance of the application by changing colors.",
            style="Pixel.TLabel",
            wraplength=400,
        )
        desc_label.pack(pady=(0, 10))

        # กรอบการตั้งค่าสีหลัก
        main_colors_frame = ttk.LabelFrame(
            self.main_frame,
            text="Main UI Colors",
            style="Pixel.TLabelframe",
            padding=10,
        )
        main_colors_frame.pack(fill="x", pady=5)

        # สร้างตัวเลือกสีต่างๆ
        self.create_color_picker(
            main_colors_frame,
            "Primary Color:",
            "primary",
            self.ui_colors.get("primary", "#3498db"),
        )

        self.create_color_picker(
            main_colors_frame,
            "Background Color:",
            "background",
            self.ui_colors.get("background", "#f5f5f5"),
        )

        # กรอบการตั้งค่าสีสถานะ
        status_colors_frame = ttk.LabelFrame(
            self.main_frame, text="Status Colors", style="Pixel.TLabelframe", padding=10
        )
        status_colors_frame.pack(fill="x", pady=5)

        self.create_color_picker(
            status_colors_frame,
            "Success Color:",
            "success",
            self.ui_colors.get("success", "#2ecc71"),
        )

        self.create_color_picker(
            status_colors_frame,
            "Warning Color:",
            "warning",
            self.ui_colors.get("warning", "#f39c12"),
        )

        self.create_color_picker(
            status_colors_frame,
            "Danger Color:",
            "danger",
            self.ui_colors.get("danger", "#e74c3c"),
        )

        # ปุ่มดูตัวอย่าง
        preview_frame = ttk.Frame(self.main_frame, style="Pixel.TFrame")
        preview_frame.pack(fill="x", pady=10)

        preview_button = ttk.Button(
            preview_frame,
            text="Preview Colors",
            command=self.show_color_preview,
            style="Pixel.TButton",
        )
        preview_button.pack(pady=5)

        # คำแนะนำ
        tip_label = ttk.Label(
            self.main_frame,
            text="TIP: Changes will take effect after saving and restarting the application.",
            style="PixelWarning.TLabel",
            justify="left",
        )
        tip_label.pack(anchor="w", pady=5)

    def create_color_picker(self, parent, label, color_key, default_color):
        """สร้างตัวเลือกสีและเก็บไว้ในลิสต์"""
        color_picker = PixelColorPicker(
            parent,
            label,
            default_color,
            command=partial(self.on_color_change, color_key),
        )
        self.color_pickers[color_key] = color_picker
        return color_picker

    def on_color_change(self, color_key, color):
        """จัดการเมื่อมีการเปลี่ยนสี"""
        self.ui_colors[color_key] = color

    def show_color_preview(self):
        """แสดงตัวอย่างการใช้สีที่เลือก"""
        preview = tk.Toplevel(self.parent)
        preview.title("Color Preview")
        preview.geometry("400x300")

        # ใช้สีพื้นหลังที่เลือก
        bg_color = self.color_pickers["background"].get_color()
        preview.configure(bg=bg_color)

        # สร้างตัวอย่างปุ่มและข้อความ
        frame = ttk.Frame(preview, padding=20)
        frame.pack(fill="both", expand=True)

        # หัวข้อ
        title = ttk.Label(
            frame, text="Color Preview", font=(UI_CONSTANTS["FONT_FAMILY"], 16, "bold")
        )
        title.pack(pady=10)

        # ตัวอย่างสี Primary
        primary_color = self.color_pickers["primary"].get_color()
        primary_frame = tk.Frame(frame, bg=primary_color, width=80, height=30)
        primary_frame.pack(pady=5)
        primary_label = ttk.Label(frame, text="Primary Color")
        primary_label.pack()

        # ตัวอย่างปุ่มต่างๆ
        buttons_frame = ttk.Frame(frame)
        buttons_frame.pack(pady=10)

        success_color = self.color_pickers["success"].get_color()
        success_button = tk.Button(
            buttons_frame, text="Success", bg=success_color, fg="#ffffff", width=10
        )
        success_button.pack(side="left", padx=5)

        warning_color = self.color_pickers["warning"].get_color()
        warning_button = tk.Button(
            buttons_frame, text="Warning", bg=warning_color, fg="#ffffff", width=10
        )
        warning_button.pack(side="left", padx=5)

        danger_color = self.color_pickers["danger"].get_color()
        danger_button = tk.Button(
            buttons_frame, text="Danger", bg=danger_color, fg="#ffffff", width=10
        )
        danger_button.pack(side="left", padx=5)

        # ปุ่มปิด
        close_button = ttk.Button(frame, text="Close Preview", command=preview.destroy)
        close_button.pack(pady=10)

    def get_settings(self):
        """รับค่าการตั้งค่าสีปัจจุบัน"""
        return {
            "ui_colors": {
                "primary": self.color_pickers["primary"].get_color(),
                "success": self.color_pickers["success"].get_color(),
                "warning": self.color_pickers["warning"].get_color(),
                "danger": self.color_pickers["danger"].get_color(),
                "background": self.color_pickers["background"].get_color(),
            }
        }

    def update_settings(self, config):
        """อัปเดตการตั้งค่าจาก config"""
        ui_colors = config.get(
            "ui_colors",
            {
                "primary": "#3498db",
                "success": "#2ecc71",
                "danger": "#e74c3c",
                "warning": "#f39c12",
                "background": "#f5f5f5",
            },
        )

        for color_key, color_value in ui_colors.items():
            if color_key in self.color_pickers:
                self.color_pickers[color_key].update_color(color_value)


class TimingSettings:
    """ส่วนการตั้งค่าเวลาต่างๆ"""

    def __init__(self, parent, config):
        """
        สร้างส่วนตั้งค่าเวลา

        Args:
            parent: Widget ที่จะเป็น parent
            config: ข้อมูลการตั้งค่าปัจจุบัน
        """
        self.parent = parent
        self.config = config

        # สร้างเฟรมหลัก
        self.main_frame = ttk.Frame(parent, style="Pixel.TFrame", padding=10)
        self.main_frame.pack(fill="both", expand=True)

        # หัวข้อ
        title_label = ttk.Label(
            self.main_frame, text="Timing Settings", style="PixelTitle.TLabel"
        )
        title_label.pack(pady=(0, 10))

        # คำอธิบาย
        desc_label = ttk.Label(
            self.main_frame,
            text="Adjust timing parameters for actions and delays.",
            style="Pixel.TLabel",
            wraplength=400,
        )
        desc_label.pack(pady=(0, 10))

        # กรอบการตั้งค่าคูลดาวน์
        cooldown_frame = ttk.LabelFrame(
            self.main_frame,
            text="Action Cooldown",
            style="Pixel.TLabelframe",
            padding=10,
        )
        cooldown_frame.pack(fill="x", pady=5)

        # สไลเดอร์สำหรับคูลดาวน์การทำงาน
        self.action_cooldown_slider = PixelSlider(
            cooldown_frame,
            "Action Cooldown (sec):",
            0.05,
            0.5,
            self.config.get("action_cooldown", 0.1),
            decimal_places=2,
        )

        # กรอบการตั้งค่าการคลิก
        click_frame = ttk.LabelFrame(
            self.main_frame, text="Click Timing", style="Pixel.TLabelframe", padding=10
        )
        click_frame.pack(fill="x", pady=5)

        # สไลเดอร์สำหรับดีเลย์การคลิกครั้งแรก
        self.first_click_delay_slider = PixelSlider(
            click_frame,
            "First Click Delay (sec):",
            0.1,
            3.0,
            self.config.get("first_click_delay", 1.0),
            decimal_places=1,
        )

        # สไลเดอร์สำหรับช่วงเวลาการคลิกแบบต่อเนื่อง
        self.periodic_click_interval_slider = PixelSlider(
            click_frame,
            "Periodic Click Interval (sec):",
            1.0,
            10.0,
            self.config.get("periodic_click_interval", 4.0),
            decimal_places=1,
        )

        # คำแนะนำ
        tip_frame = ttk.Frame(self.main_frame, style="Pixel.TFrame")
        tip_frame.pack(fill="x", pady=10)

        tip_label = ttk.Label(
            tip_frame,
            text="TIP: Lower action cooldown = faster response but higher CPU usage\nHigher click intervals = less aggressive clicking pattern",
            style="PixelWarning.TLabel",
            justify="left",
        )
        tip_label.pack(anchor="w")

    def get_settings(self):
        """รับค่าการตั้งค่าเวลาปัจจุบัน"""
        return {
            "action_cooldown": self.action_cooldown_slider.get_value(),
            "first_click_delay": self.first_click_delay_slider.get_value(),
            "periodic_click_interval": self.periodic_click_interval_slider.get_value(),
        }

    def update_settings(self, config):
        """อัปเดตการตั้งค่าจาก config"""
        self.action_cooldown_slider.set_value(config.get("action_cooldown", 0.1))
        self.first_click_delay_slider.set_value(config.get("first_click_delay", 1.0))
        self.periodic_click_interval_slider.set_value(
            config.get("periodic_click_interval", 4.0)
        )
