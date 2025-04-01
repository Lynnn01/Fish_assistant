import tkinter as tk
from tkinter import ttk
import threading
import random
import math
import time

from ui.gauge_widget import PixelGauge
from ui.progress_bar import PixelProgressBar
from ui.tooltip import PixelTooltip
from ui.styles import apply_styles
from utils.constants import PIXEL_COLORS, UI_CONSTANTS, TIPS


class PixelatedUI:
    # แก้ไขวิธีการใช้สีใน pixelated_ui.py
    # แก้ไข __init__ ใน pixelated_ui.py เพิ่มเติม
    def __init__(self, root, app):
        """
        สร้างอินเตอร์เฟซแบบพิกเซลอาร์ตสำหรับโปรแกรม Fishing Bot

        Args:
            root: หน้าต่างหลัก
            app: แอปพลิเคชันหลัก
        """
        self.root = root
        self.app = app

        # ตั้งค่าให้หน้าต่างอยู่บนสุดเสมอ
        self.root.attributes("-topmost", True)

        # เก็บ reference ของสีที่ใช้บ่อยไว้เพื่อความสะดวกและประสิทธิภาพ
        # (เรียกใช้จาก PIXEL_COLORS เพียงครั้งเดียว)
        self.primary_color = PIXEL_COLORS["PRIMARY_BLUE"]
        self.secondary_color = PIXEL_COLORS["SECONDARY_SALMON"]
        self.success_color = PIXEL_COLORS["SUCCESS_GREEN"]
        self.danger_color = PIXEL_COLORS["DANGER_RED"]
        self.warning_color = PIXEL_COLORS["WARNING_YELLOW"]
        self.bg_color = PIXEL_COLORS["BACKGROUND_DARK"]
        self.text_color = PIXEL_COLORS["TEXT_LIGHT"]
        self.panel_bg = PIXEL_COLORS["PANEL_BG"]
        self.accent_color = PIXEL_COLORS["ACCENT_BLUE"]
        self.crt_color = PIXEL_COLORS["TEXT_LIGHT"]

        # ตัวแปรติดตามตำแหน่ง
        self.last_position = 0.5

        # ตั้งค่าหน้าต่างสำหรับสไตล์พิกเซลอาร์ต
        self.root.configure(bg=self.bg_color)
        self.root.option_add(
            "*Font", f"{UI_CONSTANTS['FONT_FAMILY']} 10"
        )  # ฟอนต์แบบพิกเซล

        # ตั้งชื่อและไอคอนหน้าต่าง
        self.root.title("Fishing Assistant")
        try:
            self.root.iconbitmap("assets/fish.ico")
        except:
            pass  # ไม่มีไอคอน

        # สร้างส่วนประกอบของ UI
        apply_styles(ttk.Style())
        self.create_ui()

        # เริ่มการเคลื่อนไหวตัวชี้เกจ
        self.start_animation()

    def create_ui(self):
        """สร้างส่วนประกอบของอินเตอร์เฟซแบบพิกเซลอาร์ต"""
        # เฟรมหลัก
        main_frame = ttk.Frame(
            self.root, style="Pixel.TFrame", padding=UI_CONSTANTS["PADDING"]
        )
        main_frame.pack(fill="both", expand=True)

        # สร้างส่วนต่างๆ ของอินเตอร์เฟซ
        self._create_header_section(main_frame)
        self._create_tip_section(main_frame)
        self._create_status_section(main_frame)
        self._create_controls_section(main_frame)
        self._create_gauge_section(main_frame)
        self._create_footer_section(main_frame)

    def _create_header_section(self, parent):
        """สร้างส่วนหัวของอินเตอร์เฟซ"""
        header_frame = ttk.Frame(parent, style="PixelPanel.TFrame")
        header_frame.pack(fill="x", pady=(0, 15), ipady=5)

        # ส่วนของตัวละคร (ไม่มีในเวอร์ชันนี้)
        character_frame = tk.Frame(header_frame, bg=self.panel_bg)
        character_frame.pack(pady=(10, 5))

        # ชื่อโปรแกรมแบบเรโทร
        title_label = tk.Label(
            header_frame,
            text="╔═════════════════════════╗\n"
            "║    FISHING ASSISTANT    ║\n"
            "╚═════════════════════════╝",
            font=(UI_CONSTANTS["FONT_FAMILY"], 14, "bold"),
            fg=self.crt_color,
            bg=self.panel_bg,
            justify="center",
        )
        title_label.pack(pady=(0, 10))

    def _create_tip_section(self, parent):
        """สร้างส่วนแสดงคำแนะนำ"""
        tip_frame = ttk.Frame(parent, style="Pixel.TFrame")
        tip_frame.pack(fill="x", pady=5)

        # กรอบแบบพิกเซลสำหรับคำแนะนำ
        tip_box = tk.Frame(
            tip_frame,
            bg=self.bg_color,
            highlightbackground=self.crt_color,
            highlightthickness=1,
            padx=10,
            pady=5,
        )
        tip_box.pack(fill="x", padx=5, pady=5)

        tip_text = tk.Label(
            tip_box,
            text=TIPS["GAUGE_SELECTION"],
            fg=self.crt_color,
            bg=self.bg_color,
            font=(UI_CONSTANTS["FONT_FAMILY"], 10, "bold"),
        )
        tip_text.pack(pady=5)

    def _create_status_section(self, parent):
        """สร้างส่วนแสดงสถานะ"""
        status_frame = ttk.LabelFrame(
            parent, text="STATUS", style="Pixel.TLabelframe", padding=10
        )
        status_frame.pack(fill="x", pady=10)

        # คอลัมน์สถานะ
        status_columns = ttk.Frame(status_frame, style="Pixel.TFrame")
        status_columns.pack(fill="x")

        # คอลัมน์ซ้าย - สถานะ
        left_status = ttk.Frame(status_columns, style="Pixel.TFrame")
        left_status.pack(side="top", fill="x", expand=True)

        status_label_title = ttk.Label(
            left_status, text="█ STATUS:", style="Pixel.TLabel"
        )
        status_label_title.pack(side="left", padx=5)

        self.status_label = ttk.Label(left_status, text="READY", style="Pixel.TLabel")
        self.status_label.pack(side="left", padx=5)

        # คอลัมน์ขวา - พื้นที่ที่เลือก
        right_status = ttk.Frame(status_columns, style="Pixel.TFrame")
        right_status.pack(side="top", fill="x", expand=True, pady=5)

        region_label_title = ttk.Label(
            right_status, text="█ REGION:", style="Pixel.TLabel"
        )
        region_label_title.pack(side="left", padx=5)

        self.region_label = ttk.Label(
            right_status, text="NO REGION SELECTED", style="Pixel.TLabel"
        )
        self.region_label.pack(side="left", padx=5)

        # ใช้ PixelProgressBar แทน custom progress bar เดิม
        progress_frame = ttk.Frame(status_frame, style="Pixel.TFrame")
        progress_frame.pack(fill="x", pady=(10, 0))

        colors = {
            "bg": self.bg_color,
            "text": self.text_color,
            "panel_bg": self.panel_bg,
            "success": self.success_color,
            "danger": self.danger_color,
            "warning": self.warning_color,
        }

        self.progress_bar = PixelProgressBar(progress_frame, colors, height=15)

    def _create_controls_section(self, parent):
        """สร้างส่วนควบคุม"""
        control_frame = ttk.LabelFrame(
            parent, text="CONTROLS", style="Pixel.TLabelframe", padding=10
        )
        control_frame.pack(fill="x", pady=10)

        button_frame = ttk.Frame(control_frame, style="Pixel.TFrame")
        button_frame.pack(fill="x", pady=5)

        # กำหนดคอลัมน์
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)

        # ปุ่มแบบพิกเซล
        self.select_button = ttk.Button(
            button_frame,
            text="[ SELECT REGION ]",
            command=self.app.select_gauge_region,
            style="Pixel.TButton",
        )
        self.select_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.start_button = ttk.Button(
            button_frame,
            text="[ START ]",
            command=self.app.start_fishing,
            state="disabled",
            style="PixelSuccess.TButton",
        )
        self.start_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.stop_button = ttk.Button(
            button_frame,
            text="[ STOP ]",
            command=self.app.stop_fishing,
            state="disabled",
            style="PixelDanger.TButton",
        )
        self.stop_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

    # แก้ไข method _create_gauge_section ใน pixelated_ui.py

    def _create_gauge_section(self, parent):
        """สร้างส่วนแสดงเกจ"""
        gauge_frame = ttk.LabelFrame(
            parent, text="GAUGE", style="Pixel.TLabelframe", padding=10
        )
        gauge_frame.pack(fill="x", pady=10)

        # ตั้งค่าสีของเกจจาก constants โดยตรง
        gauge_colors = {
            "success": PIXEL_COLORS["SUCCESS_GREEN"],
            "danger": PIXEL_COLORS["DANGER_RED"],
            "warning": PIXEL_COLORS["WARNING_YELLOW"],
            "bg": PIXEL_COLORS["BACKGROUND_DARK"],
            "accent": PIXEL_COLORS["ACCENT_BLUE"],
            "crt": PIXEL_COLORS["TEXT_LIGHT"],
        }

        # สร้างเกจแบบพิกเซล
        self.gauge = PixelGauge(gauge_frame, gauge_colors)

        # สร้างส่วนแสดงข้อมูล
        indicator_frame = ttk.Frame(gauge_frame, style="Pixel.TFrame")
        indicator_frame.pack(fill="x")

        # แบ่งเป็น 2 คอลัมน์
        indicator_frame.columnconfigure(0, weight=1)
        indicator_frame.columnconfigure(1, weight=1)

        # ซ้าย - ตำแหน่ง
        left_info = ttk.Frame(indicator_frame, style="Pixel.TFrame")
        left_info.grid(row=0, column=0, sticky="w")

        position_label = ttk.Label(left_info, text="POSITION:", style="Pixel.TLabel")
        position_label.pack(side="left", padx=2)

        self.position_value = ttk.Label(left_info, text="CENTER", style="Pixel.TLabel")
        self.position_value.pack(side="left", padx=2)

        # ขวา - โซน
        right_info = ttk.Frame(indicator_frame, style="Pixel.TFrame")
        right_info.grid(row=0, column=1, sticky="e")

        zone_label = ttk.Label(right_info, text="ZONE:", style="Pixel.TLabel")
        zone_label.pack(side="left", padx=2)

        # ใช้ style แทนการกำหนดสีโดยตรง
        self.zone_value = ttk.Label(
            right_info, text="SAFE", style="PixelSuccess.TLabel"
        )
        self.zone_value.pack(side="left", padx=2)

    def _create_footer_section(self, parent):
        """สร้างส่วนท้ายของอินเตอร์เฟซ"""
        footer_frame = ttk.Frame(parent, style="Pixel.TFrame")
        footer_frame.pack(fill="x", pady=(10, 0))

        # ป้ายแสดงคีย์ลัด
        hotkey_label = tk.Label(
            footer_frame,  # แก้ไขปัญหาไม่ได้ระบุ parent
            text="╔═════════════════════════════╗\n"
            f"║  {TIPS['HOTKEY_INFO']}  ║\n"
            "╚═════════════════════════════╝",
            foreground=self.danger_color,
            background=self.bg_color,
            font=(UI_CONSTANTS["FONT_FAMILY"], 10, "bold"),
        )
        hotkey_label.pack(pady=5)

        # เวอร์ชันพร้อมตกแต่งแบบพิกเซล
        version_frame = tk.Frame(footer_frame, bg=self.bg_color)
        version_frame.pack(side="right", padx=5)

        version_label = tk.Label(
            version_frame,
            text="[v1.0]",
            fg=self.accent_color,
            bg=self.bg_color,
            font=(UI_CONSTANTS["FONT_FAMILY"], 8),
        )
        version_label.pack(side="right")

    # แก้ไข method update_line_position ใน pixelated_ui.py

    def update_line_position(self, relative_pos):
        """อัปเดตตำแหน่งเส้นตัวชี้ในเกจ"""
        # ใช้ gauge widget สำหรับการอัปเดตตำแหน่ง
        zone_type, position_text = self.gauge.update_position(relative_pos)

        # อัปเดตข้อความตำแหน่ง
        self.position_value.config(text=position_text)

        # อัปเดตข้อความโซนด้วย style แทนการกำหนดสีโดยตรง
        if zone_type == "danger":
            self.zone_value.config(text="DANGER", style="PixelDanger.TLabel")
        elif zone_type == "warning":
            self.zone_value.config(text="CAUTION", style="PixelWarning.TLabel")
        else:
            self.zone_value.config(text="SAFE", style="PixelSuccess.TLabel")

        # บันทึกตำแหน่งปัจจุบันเพื่อคำนวณความเร็ว
        if hasattr(self, "last_position"):
            self.last_position = relative_pos

    def update_status(self, text, status_type="normal"):
        """อัปเดตข้อความสถานะพร้อมเอฟเฟกต์"""
        self.status_label.config(text=text.upper())

        if status_type == "success":
            self.status_label.config(foreground=self.success_color)
            self.progress_bar.update(100)  # ใช้ progress_bar ที่เป็นคลาสแยก
        elif status_type == "danger":
            self.status_label.config(foreground=self.danger_color)
            self.progress_bar.update(0)
        elif status_type == "warning":
            self.status_label.config(foreground=self.warning_color)
            # ใช้การแสดงผลแบบเคลื่อนไหว
            self.progress_bar.start_animation()
        else:
            self.status_label.config(foreground=self.text_color)
            self.progress_bar.update(50)

    def update_region_info(self, region):
        """อัปเดตข้อมูลพื้นที่ที่เลือกพร้อมเอฟเฟกต์"""
        if region:
            x1, y1, x2, y2 = region
            size = f"{x2-x1}x{y2-y1}"
            self.region_label.config(text=f"({x1},{y1})-({x2},{y2}) [{size}]")

            # แสดง tooltip แบบพิกเซล
            colors = {"bg": self.bg_color, "text": self.crt_color}
            PixelTooltip(self.root, f"REGION SELECTED: {size}", colors)

            # แสดงผลการเลือกพื้นที่สำเร็จ
            self.progress_bar.pulse(100, 1000)

    def set_start_button_state(self, state):
        """ตั้งค่าสถานะปุ่ม Start พร้อมเอฟเฟกต์ทางสายตา"""
        print(f"Setting start button state to: {state}")

        # ตั้งค่าสถานะโดยตรง
        self.start_button.config(state=state)

        # เพิ่มเอฟเฟกต์หากจำเป็น
        if state == "normal" and self.start_button.cget("state") != "disabled":
            self.blink_button(self.start_button, 3)

    def blink_button(self, button, times=3):
        """สร้างเอฟเฟกต์กะพริบให้ปุ่ม"""
        if times <= 0:
            return

        # สลับสไตล์ของปุ่ม
        current_style = button.cget("style")
        if current_style == "PixelSuccess.TButton":
            button.config(style="Pixel.TButton")
        else:
            button.config(style="PixelSuccess.TButton")

        # ทำซ้ำอีกครั้ง
        self.root.after(200, lambda: self.blink_button(button, times - 1))

    def set_button_states(self, select_state, start_state, stop_state):
        """ตั้งค่าสถานะปุ่มทั้งหมด"""
        current_stop = self.stop_button.cget("state")

        # ตั้งค่าสถานะปุ่ม
        self.select_button.config(state=select_state)
        self.start_button.config(state=start_state)
        self.stop_button.config(state=stop_state)

        # แสดงเอฟเฟกต์กะพริบสำหรับปุ่ม Stop เมื่อเปิดใช้งาน
        if stop_state == "normal" and current_stop == "disabled":
            self.blink_button(self.stop_button, 3)

    def start_animation(self):
        """เริ่มการเคลื่อนไหวเส้นตัวชี้เกจ"""
        self.is_animating = True
        self.animation_thread = threading.Thread(
            target=self._animation_loop, daemon=True
        )
        self.animation_thread.start()

    def stop_animation(self):
        """หยุดการเคลื่อนไหวทั้งหมด"""
        self.is_animating = False

        # หยุดการเคลื่อนไหวของ progress bar
        if hasattr(self, "progress_bar"):
            self.progress_bar.stop_animation()

    def _animation_loop(self):
        """ลูปการเคลื่อนไหวเส้นตัวชี้เกจแบบต่อเนื่อง"""
        # ตัวแปรสำหรับการเคลื่อนไหวแบบนุ่มนวล
        amplitude = 0.45  # ระยะห่างสูงสุดจากจุดกึ่งกลาง
        period = 15.0  # ระยะเวลาสำหรับหนึ่งรอบ

        # เวลาเริ่มต้น
        start_time = time.time()

        while self.is_animating:
            # เคลื่อนไหวเฉพาะเมื่อไม่ได้ทำงานอยู่
            if not hasattr(self.app, "running") or not self.app.running:
                # ใช้คลื่นไซน์เพื่อการเคลื่อนไหวที่ดูเป็นธรรมชาติ
                current_time = time.time() - start_time
                position = 0.5 + amplitude * math.sin(
                    2 * math.pi * current_time / period
                )

                # อัปเดตตำแหน่ง
                self.update_line_position(position)

                # สุ่มสร้างเหตุการณ์ปลากระตุกเพื่อการสาธิต
                if random.random() < 0.002:  # 0.2% โอกาสต่อเฟรม
                    self.simulate_bite()

            # หน่วงเวลาเพื่อการเคลื่อนไหวที่นุ่มนวล
            time.sleep(0.05)

    def simulate_bite(self):
        """จำลองการกระตุกของปลา"""
        # ตำแหน่งเริ่มต้น
        start_pos = 0.5

        # ใช้เกจสำหรับการจำลองการกระตุก
        self.gauge.simulate_bite(start_pos, 0.5, None)

    def show_tooltip(self, message, duration=2000):
        """แสดง tooltip แบบพิกเซล"""
        # ใช้คลาส PixelTooltip ที่แยกออกมา
        colors = {"bg": self.bg_color, "text": self.crt_color}
        PixelTooltip(self.root, message, colors, duration=duration)
