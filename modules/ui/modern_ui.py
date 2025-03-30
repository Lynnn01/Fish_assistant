import tkinter as tk
from tkinter import ttk, messagebox
import time
import cv2
import numpy as np
from PIL import Image, ImageTk
import os
import threading
from .components.tab_panel import TabPanel
from .components.notification import Notification
from .components.gauge_visualizer import GaugeVisualizer
from .components.theme_manager import ThemeManager


class ModernUI:
    def __init__(self, app):
        self.app = app
        self.root = app.root

        # สร้าง Theme Manager
        self.theme_manager = ThemeManager(self, app.config.get("theme", "light"))

        # สร้างตัวแปรสำหรับ UI elements
        self.status_indicator = None
        self.status_text = None
        self.region_label = None
        self.line_position = 0.5  # Default position (middle)
        self.gauge_visualizer = None
        self.current_notification = None
        self.notification_queue = []

        # เตรียมข้อมูลสำหรับภาพตัวอย่าง
        self.sample_image = None
        self.sample_photo = None

        # Counter variables
        self.catch_counter = tk.StringVar(value="0")
        self.detection_rate = tk.StringVar(value="0%")

    def build_interface(self):
        """สร้าง UI หลักของโปรแกรม"""
        # กำหนดสีพื้นหลัก
        self.root.configure(bg=self.theme_manager.bg_color)

        # สร้าง Header
        self.create_header()

        # สร้าง Main Content
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=15, pady=5)

        # สร้าง Tabs
        self.tab_panel = TabPanel(main_frame, self.theme_manager)

        # Tab หลัก (Main)
        main_tab = self.tab_panel.add_tab("Main", icon="🎮")
        self.build_main_tab(main_tab)

        # Tab สถิติ (Stats)
        stats_tab = self.tab_panel.add_tab("Statistics", icon="📊")
        self.build_stats_tab(stats_tab)

        # Tab ตั้งค่า (Settings)
        settings_tab = self.tab_panel.add_tab("Settings", icon="⚙️")
        self.build_settings_tab(settings_tab)

        # Tab ช่วยเหลือ (Help)
        help_tab = self.tab_panel.add_tab("Help", icon="❓")
        self.build_help_tab(help_tab)

        # สร้าง Footer
        self.create_footer()

        # เริ่มต้นอนิเมชัน
        self.start_animations()

    def create_header(self):
        """สร้างส่วนหัวของโปรแกรม"""
        header_frame = tk.Frame(
            self.root, bg=self.theme_manager.primary_color, height=60
        )
        header_frame.pack(fill="x", pady=(0, 10))

        # โลโก้หรือไอคอน
        try:
            icon_path = os.path.join("assets", "icons", "fish_icon.png")
            if os.path.exists(icon_path):
                # โหลดและปรับขนาดรูปภาพ
                logo_img = Image.open(icon_path)
                logo_img = logo_img.resize((40, 40), Image.LANCZOS)
                logo_photo = ImageTk.PhotoImage(logo_img)

                logo_label = tk.Label(
                    header_frame, image=logo_photo, bg=self.theme_manager.primary_color
                )
                logo_label.image = logo_photo  # เก็บอ้างอิงเพื่อป้องกัน garbage collection
                logo_label.pack(side="left", padx=10, pady=10)
        except Exception:
            # ถ้าไม่มีไฟล์รูปภาพ ให้ใช้ข้อความแทน
            pass

        # ชื่อโปรแกรม
        title_label = tk.Label(
            header_frame,
            text="Fishing Master Pro",
            font=("Arial", 18, "bold"),
            bg=self.theme_manager.primary_color,
            fg="white",
        )
        title_label.pack(side="left", pady=15, padx=10)

        # ปุ่มเปลี่ยนธีม
        theme_button = ttk.Button(
            header_frame, text="🌓", width=3, command=self.toggle_theme
        )
        theme_button.pack(side="right", padx=10, pady=15)

    def create_footer(self):
        """สร้างส่วนท้ายของโปรแกรม"""
        footer_frame = ttk.Frame(self.root)
        footer_frame.pack(fill="x", padx=15, pady=10)

        # ข้อความ hotkey และเวอร์ชัน
        version_label = ttk.Label(footer_frame, text="v1.0.0", font=("Arial", 8))
        version_label.pack(side="right", padx=5)

        hotkey_label = ttk.Label(
            footer_frame,
            text="Hotkeys: F6 = Start | F10 = Stop",
            foreground=self.theme_manager.warning_color,
            font=("Arial", 9, "bold"),
        )
        hotkey_label.pack(side="left", padx=5)

    def build_main_tab(self, parent):
        """สร้างแท็บหลัก (Main) สำหรับควบคุมการทำงาน"""
        # กรอบแสดงสถานะ
        status_frame = ttk.LabelFrame(parent, text="Status")
        status_frame.pack(fill="x", pady=10)

        # สร้างตัวแสดงสถานะแบบกราฟิก
        self.status_canvas = tk.Canvas(
            status_frame,
            height=30,
            bg=self.theme_manager.bg_color,
            highlightthickness=0,
        )
        self.status_canvas.pack(fill="x", pady=5, padx=5)

        self.status_indicator = self.status_canvas.create_oval(
            10, 5, 30, 25, fill="#cccccc"
        )
        self.status_text = self.status_canvas.create_text(
            40,
            15,
            text="Ready",
            anchor="w",
            font=("Arial", 10, "bold"),
            fill=self.theme_manager.text_color,
        )

        # กรอบแสดงข้อมูลพื้นที่ที่เลือก
        self.region_frame = ttk.Frame(status_frame)
        self.region_frame.pack(fill="x", pady=5)

        ttk.Label(self.region_frame, text="Region:", font=("Arial", 10, "bold")).pack(
            side="left", padx=5
        )
        self.region_label = ttk.Label(self.region_frame, text="No region selected")
        self.region_label.pack(side="left", padx=5)

        # สร้างปุ่มควบคุม
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill="x", pady=10)

        # ใช้ grid layout สำหรับปุ่ม
        control_frame.columnconfigure(0, weight=1)
        control_frame.columnconfigure(1, weight=1)
        control_frame.columnconfigure(2, weight=1)

        self.select_button = ttk.Button(
            control_frame,
            text="Select Region",
            style="Primary.TButton",
            command=lambda: self.app.detector.select_gauge_region(),
        )
        self.select_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.start_button = ttk.Button(
            control_frame,
            text="Start",
            style="Success.TButton",
            command=self.app.start_fishing,
            state="disabled",
        )
        self.start_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.stop_button = ttk.Button(
            control_frame,
            text="Stop",
            style="Danger.TButton",
            command=self.app.stop_fishing,
            state="disabled",
        )
        self.stop_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # สร้างกรอบการจำลองเกจ
        gauge_frame = ttk.LabelFrame(parent, text="Gauge Visualization")
        gauge_frame.pack(fill="x", pady=10)

        # สร้าง Gauge Visualizer Component
        self.gauge_visualizer = GaugeVisualizer(gauge_frame, self.theme_manager)

        # กรอบสำหรับภาพตัวอย่าง
        sample_frame = ttk.LabelFrame(parent, text="Sample Image")
        sample_frame.pack(fill="x", pady=10)

        # Canvas สำหรับแสดงภาพตัวอย่าง
        self.sample_canvas = tk.Canvas(
            sample_frame, height=120, bg="#333333", highlightthickness=0
        )
        self.sample_canvas.pack(fill="x", pady=10, padx=10)

        # Text instruction ถ้ายังไม่มีภาพ
        self.sample_text = self.sample_canvas.create_text(
            self.sample_canvas.winfo_reqwidth() // 2,
            60,
            text="No sample image available\nSelect a region to see preview",
            fill="white",
            justify=tk.CENTER,
            font=("Arial", 10),
        )

        # กรอบแสดงสถิติการตกปลา
        fishing_stats_frame = ttk.LabelFrame(parent, text="Fishing Stats")
        fishing_stats_frame.pack(fill="x", pady=10)

        # สร้าง Grid สำหรับสถิติ
        stats_grid = ttk.Frame(fishing_stats_frame)
        stats_grid.pack(fill="x", padx=10, pady=10)

        # คอลัมน์
        stats_grid.columnconfigure(0, weight=2)
        stats_grid.columnconfigure(1, weight=1)
        stats_grid.columnconfigure(2, weight=2)
        stats_grid.columnconfigure(3, weight=1)

        # Catches
        ttk.Label(stats_grid, text="Catches:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Label(stats_grid, textvariable=self.catch_counter, font=("Arial", 10)).grid(
            row=0, column=1, sticky="w", padx=5, pady=5
        )

        # Detection Rate
        ttk.Label(stats_grid, text="Detection Rate:", font=("Arial", 10, "bold")).grid(
            row=0, column=2, sticky="w", padx=5, pady=5
        )
        ttk.Label(
            stats_grid, textvariable=self.detection_rate, font=("Arial", 10)
        ).grid(row=0, column=3, sticky="w", padx=5, pady=5)

        # Session Time
        ttk.Label(stats_grid, text="Session Time:", font=("Arial", 10, "bold")).grid(
            row=1, column=0, sticky="w", padx=5, pady=5
        )
        self.session_time = tk.StringVar(value="00:00:00")
        ttk.Label(stats_grid, textvariable=self.session_time, font=("Arial", 10)).grid(
            row=1, column=1, sticky="w", padx=5, pady=5
        )

        # Catch Rate
        ttk.Label(stats_grid, text="Catch Rate:", font=("Arial", 10, "bold")).grid(
            row=1, column=2, sticky="w", padx=5, pady=5
        )
        self.catch_rate = tk.StringVar(value="0.0/h")
        ttk.Label(stats_grid, textvariable=self.catch_rate, font=("Arial", 10)).grid(
            row=1, column=3, sticky="w", padx=5, pady=5
        )

        # ปุ่ม Reset Counter
        ttk.Button(
            fishing_stats_frame, text="Reset Counter", command=self.reset_counter
        ).pack(side="left", padx=10, pady=5)

    def build_stats_tab(self, parent):
        """สร้างแท็บสถิติ (Statistics) สำหรับแสดงข้อมูลสถิติ"""
        # กรอบสถิติทั้งหมด
        all_time_frame = ttk.LabelFrame(parent, text="All-time Statistics")
        all_time_frame.pack(fill="x", pady=10)

        # สร้าง Grid สำหรับสถิติ
        stats_grid = ttk.Frame(all_time_frame)
        stats_grid.pack(fill="x", padx=10, pady=10)

        try:
            # โหลดสถิติ
            all_time_stats = self.app.analytics.get_all_time_stats()

            # คอลัมน์
            stats_grid.columnconfigure(0, weight=2)
            stats_grid.columnconfigure(1, weight=1)
            stats_grid.columnconfigure(2, weight=2)
            stats_grid.columnconfigure(3, weight=1)

            # Total Catches
            ttk.Label(
                stats_grid, text="Total Catches:", font=("Arial", 10, "bold")
            ).grid(row=0, column=0, sticky="w", padx=5, pady=5)
            ttk.Label(
                stats_grid,
                text=str(all_time_stats["total_catches"]),
                font=("Arial", 10),
            ).grid(row=0, column=1, sticky="w", padx=5, pady=5)

            # Total Sessions
            ttk.Label(
                stats_grid, text="Total Sessions:", font=("Arial", 10, "bold")
            ).grid(row=0, column=2, sticky="w", padx=5, pady=5)
            ttk.Label(
                stats_grid,
                text=str(all_time_stats["total_sessions"]),
                font=("Arial", 10),
            ).grid(row=0, column=3, sticky="w", padx=5, pady=5)

            # Total Time
            ttk.Label(stats_grid, text="Total Time:", font=("Arial", 10, "bold")).grid(
                row=1, column=0, sticky="w", padx=5, pady=5
            )

            # แปลงเวลาเป็นรูปแบบที่อ่านง่าย
            total_hours = int(all_time_stats["total_time"] // 3600)
            total_minutes = int((all_time_stats["total_time"] % 3600) // 60)
            time_text = f"{total_hours}h {total_minutes}m"

            ttk.Label(stats_grid, text=time_text, font=("Arial", 10)).grid(
                row=1, column=1, sticky="w", padx=5, pady=5
            )

            # Total Clicks
            ttk.Label(
                stats_grid, text="Total Clicks:", font=("Arial", 10, "bold")
            ).grid(row=1, column=2, sticky="w", padx=5, pady=5)
            ttk.Label(
                stats_grid, text=str(all_time_stats["total_clicks"]), font=("Arial", 10)
            ).grid(row=1, column=3, sticky="w", padx=5, pady=5)

            # Best Session
            best_frame = ttk.LabelFrame(parent, text="Best Session")
            best_frame.pack(fill="x", pady=10)

            best_grid = ttk.Frame(best_frame)
            best_grid.pack(fill="x", padx=10, pady=10)

            # คอลัมน์
            best_grid.columnconfigure(0, weight=2)
            best_grid.columnconfigure(1, weight=1)
            best_grid.columnconfigure(2, weight=2)
            best_grid.columnconfigure(3, weight=1)

            best_session = all_time_stats["best_session"]

            # Date
            ttk.Label(best_grid, text="Date:", font=("Arial", 10, "bold")).grid(
                row=0, column=0, sticky="w", padx=5, pady=5
            )
            ttk.Label(best_grid, text=best_session["date"], font=("Arial", 10)).grid(
                row=0, column=1, sticky="w", padx=5, pady=5
            )

            # Catches
            ttk.Label(best_grid, text="Catches:", font=("Arial", 10, "bold")).grid(
                row=0, column=2, sticky="w", padx=5, pady=5
            )
            ttk.Label(
                best_grid, text=str(best_session["catches"]), font=("Arial", 10)
            ).grid(row=0, column=3, sticky="w", padx=5, pady=5)

            # Duration
            ttk.Label(best_grid, text="Duration:", font=("Arial", 10, "bold")).grid(
                row=1, column=0, sticky="w", padx=5, pady=5
            )

            # แปลงเวลาเป็นรูปแบบที่อ่านง่าย
            duration_hours = int(best_session["duration"] // 3600)
            duration_minutes = int((best_session["duration"] % 3600) // 60)
            duration_text = f"{duration_hours}h {duration_minutes}m"

            ttk.Label(best_grid, text=duration_text, font=("Arial", 10)).grid(
                row=1, column=1, sticky="w", padx=5, pady=5
            )

            # Catch Rate
            ttk.Label(best_grid, text="Catch Rate:", font=("Arial", 10, "bold")).grid(
                row=1, column=2, sticky="w", padx=5, pady=5
            )

            if best_session["duration"] > 0:
                rate = (best_session["catches"] / best_session["duration"]) * 3600
                rate_text = f"{rate:.1f}/h"
            else:
                rate_text = "N/A"

            ttk.Label(best_grid, text=rate_text, font=("Arial", 10)).grid(
                row=1, column=3, sticky="w", padx=5, pady=5
            )

            # กรอบประวัติการใช้งาน
            history_frame = ttk.LabelFrame(parent, text="Session History")
            history_frame.pack(fill="both", expand=True, pady=10)

            # สร้าง Treeview สำหรับแสดงประวัติ
            columns = ("date", "catches", "duration", "rate")
            history_tree = ttk.Treeview(history_frame, columns=columns, show="headings")

            # กำหนดหัวข้อคอลัมน์
            history_tree.heading("date", text="Date")
            history_tree.heading("catches", text="Catches")
            history_tree.heading("duration", text="Duration")
            history_tree.heading("rate", text="Rate (fish/h)")

            # กำหนดความกว้างคอลัมน์
            history_tree.column("date", width=150)
            history_tree.column("catches", width=80)
            history_tree.column("duration", width=80)
            history_tree.column("rate", width=100)

            # เพิ่ม Scrollbar
            scrollbar = ttk.Scrollbar(
                history_frame, orient="vertical", command=history_tree.yview
            )
            history_tree.configure(yscrollcommand=scrollbar.set)

            # จัดวาง
            history_tree.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            # เพิ่มข้อมูลประวัติ
            for session in reversed(all_time_stats["history"]):
                # แปลงระยะเวลา
                hours = int(session["duration"] // 3600)
                minutes = int((session["duration"] % 3600) // 60)
                duration_str = f"{hours}h {minutes}m"

                # คำนวณอัตรา
                if session["duration"] > 0:
                    rate = (session["catches"] / session["duration"]) * 3600
                    rate_str = f"{rate:.1f}"
                else:
                    rate_str = "N/A"

                history_tree.insert(
                    "",
                    "end",
                    values=(
                        session["date"],
                        session["catches"],
                        duration_str,
                        rate_str,
                    ),
                )

            # ปุ่มสำหรับ Export สถิติ
            button_frame = ttk.Frame(parent)
            button_frame.pack(fill="x", pady=10)

            ttk.Button(
                button_frame, text="Export Statistics", command=self.export_statistics
            ).pack(side="left", padx=5)
            ttk.Button(
                button_frame,
                text="Reset All Statistics",
                command=self.reset_all_statistics,
            ).pack(side="right", padx=5)
        except Exception as e:
            # ในกรณีที่ยังโหลดข้อมูลไม่ได้ แสดงข้อความแทน
            ttk.Label(
                stats_grid,
                text=f"Statistics will be available after first use.",
                font=("Arial", 10),
            ).pack(pady=20)

    def build_settings_tab(self, parent):
        """สร้างแท็บการตั้งค่า (Settings)"""
        # สร้าง Notebook สำหรับแบ่งหมวดหมู่การตั้งค่า
        settings_notebook = ttk.Notebook(parent)
        settings_notebook.pack(fill="both", expand=True, pady=10)

        # แท็บการตั้งค่าหลัก
        general_tab = ttk.Frame(settings_notebook)
        settings_notebook.add(general_tab, text="General")

        # แท็บการตั้งค่าการตรวจจับ
        detection_tab = ttk.Frame(settings_notebook)
        settings_notebook.add(detection_tab, text="Detection")

        # แท็บการตั้งค่าคีย์ลัด
        hotkeys_tab = ttk.Frame(settings_notebook)
        settings_notebook.add(hotkeys_tab, text="Hotkeys")

        # แท็บการตั้งค่าขั้นสูง
        advanced_tab = ttk.Frame(settings_notebook)
        settings_notebook.add(advanced_tab, text="Advanced")

        # สร้างเนื้อหาแต่ละแท็บ
        self.build_general_settings(general_tab)
        self.build_detection_settings(detection_tab)
        self.build_hotkey_settings(hotkeys_tab)
        self.build_advanced_settings(advanced_tab)

        # ปุ่มบันทึกการตั้งค่า
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x", pady=10)

        ttk.Button(
            button_frame,
            text="Save Settings",
            command=self.app.save_settings,
            style="Primary.TButton",
        ).pack(side="right", padx=5)
        ttk.Button(
            button_frame,
            text="Reset to Default",
            command=self.reset_to_default_settings,
        ).pack(side="left", padx=5)

    def build_general_settings(self, parent):
        """สร้างการตั้งค่าทั่วไป"""
        # กรอบการตั้งค่า UI
        ui_frame = ttk.LabelFrame(parent, text="User Interface")
        ui_frame.pack(fill="x", padx=10, pady=10)

        # Theme
        theme_frame = ttk.Frame(ui_frame)
        theme_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(theme_frame, text="Theme:").pack(side="left", padx=5)

        theme_var = tk.StringVar(value=self.app.config.get("theme", "light"))
        theme_combo = ttk.Combobox(
            theme_frame, textvariable=theme_var, state="readonly"
        )
        theme_combo["values"] = ("light", "dark", "blue", "green")
        theme_combo.pack(side="left", padx=5)

        def on_theme_change(event):
            self.theme_manager.set_theme(theme_var.get())

        theme_combo.bind("<<ComboboxSelected>>", on_theme_change)

        # Animation Speed
        anim_frame = ttk.Frame(ui_frame)
        anim_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(anim_frame, text="Animation Speed:").pack(side="left", padx=5)

        animation_var = tk.IntVar(value=self.app.config.get("animation_speed", 5))
        animation_scale = ttk.Scale(
            anim_frame, from_=0, to=10, orient="horizontal", variable=animation_var
        )
        animation_scale.pack(side="left", fill="x", expand=True, padx=5)

        ttk.Label(anim_frame, textvariable=animation_var).pack(side="left", padx=5)

        # Sound Alerts
        sound_frame = ttk.Frame(ui_frame)
        sound_frame.pack(fill="x", padx=5, pady=5)

        sound_var = tk.BooleanVar(value=self.app.config.get("sound_alerts", True))
        sound_check = ttk.Checkbutton(
            sound_frame, text="Enable Sound Alerts", variable=sound_var
        )
        sound_check.pack(side="left", padx=5)

        # Minimize to Tray
        tray_frame = ttk.Frame(ui_frame)
        tray_frame.pack(fill="x", padx=5, pady=5)

        tray_var = tk.BooleanVar(value=self.app.config.get("minimize_to_tray", False))
        tray_check = ttk.Checkbutton(
            tray_frame, text="Minimize to System Tray", variable=tray_var
        )
        tray_check.pack(side="left", padx=5)

        # กรอบการตั้งค่าการคลิก
        click_frame = ttk.LabelFrame(parent, text="Click Settings")
        click_frame.pack(fill="x", padx=10, pady=10)

        # Action Cooldown
        cooldown_frame = ttk.Frame(click_frame)
        cooldown_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(cooldown_frame, text="Action Cooldown (sec):").pack(
            side="left", padx=5
        )

        cooldown_var = tk.DoubleVar(value=self.app.config.get("action_cooldown", 0.1))
        cooldown_scale = ttk.Scale(
            cooldown_frame,
            from_=0.05,
            to=0.5,
            orient="horizontal",
            variable=cooldown_var,
        )
        cooldown_scale.pack(side="left", fill="x", expand=True, padx=5)

        # แสดงค่าทศนิยม 2 ตำแหน่ง
        cooldown_label_var = tk.StringVar()

        def update_cooldown_label(*args):
            cooldown_label_var.set(f"{cooldown_var.get():.2f}")

        cooldown_var.trace_add("write", update_cooldown_label)
        update_cooldown_label()

        ttk.Label(cooldown_frame, textvariable=cooldown_label_var).pack(
            side="left", padx=5
        )

        # Double Click
        double_click_frame = ttk.Frame(click_frame)
        double_click_frame.pack(fill="x", padx=5, pady=5)

        double_click_var = tk.BooleanVar(
            value=self.app.config.get("double_click", False)
        )
        double_click_check = ttk.Checkbutton(
            double_click_frame, text="Enable Double Click", variable=double_click_var
        )
        double_click_check.pack(side="left", padx=5)

        # Double Click Delay
        double_click_delay_frame = ttk.Frame(click_frame)
        double_click_delay_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(double_click_delay_frame, text="Double Click Delay (sec):").pack(
            side="left", padx=5
        )

        double_click_delay_var = tk.DoubleVar(
            value=self.app.config.get("double_click_delay", 0.1)
        )
        double_click_delay_scale = ttk.Scale(
            double_click_delay_frame,
            from_=0.05,
            to=0.5,
            orient="horizontal",
            variable=double_click_delay_var,
        )
        double_click_delay_scale.pack(side="left", fill="x", expand=True, padx=5)

        # แสดงค่าทศนิยม 2 ตำแหน่ง
        double_click_delay_label_var = tk.StringVar()

        def update_double_click_delay_label(*args):
            double_click_delay_label_var.set(f"{double_click_delay_var.get():.2f}")

        double_click_delay_var.trace_add("write", update_double_click_delay_label)
        update_double_click_delay_label()

        ### modules/ui/modern_ui.py (continued)
        ttk.Label(
            double_click_delay_frame, textvariable=double_click_delay_label_var
        ).pack(side="left", padx=5)

        # เชื่อมการแสดงผลกับการเปิด/ปิด Double Click
        def toggle_double_click_delay(*args):
            if double_click_var.get():
                double_click_delay_scale.config(state="normal")
            else:
                double_click_delay_scale.config(state="disabled")

        double_click_var.trace_add("write", toggle_double_click_delay)
        toggle_double_click_delay()  # เรียกครั้งแรกเพื่อตั้งค่าเริ่มต้น

        # สร้างฟังก์ชันเพื่อเก็บการตั้งค่าทั้งหมด
        def get_general_settings():
            return {
                "theme": theme_var.get(),
                "animation_speed": animation_var.get(),
                "sound_alerts": sound_var.get(),
                "minimize_to_tray": tray_var.get(),
                "action_cooldown": cooldown_var.get(),
                "double_click": double_click_var.get(),
                "double_click_delay": double_click_delay_var.get(),
            }

        # เก็บฟังก์ชันไว้ในออบเจ็กต์เพื่อเรียกใช้ภายหลัง
        parent.get_settings = get_general_settings

    def build_detection_settings(self, parent):
        """สร้างการตั้งค่าการตรวจจับ"""
        # กรอบการตั้งค่าการตรวจจับ
        detection_frame = ttk.LabelFrame(parent, text="Detection Settings")
        detection_frame.pack(fill="x", padx=10, pady=10)

        # Color Sensitivity
        color_frame = ttk.Frame(detection_frame)
        color_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(color_frame, text="Color Sensitivity:").pack(side="left", padx=5)

        color_var = tk.IntVar(value=self.app.config.get("green_tolerance", 30))
        color_scale = ttk.Scale(
            color_frame, from_=10, to=50, orient="horizontal", variable=color_var
        )
        color_scale.pack(side="left", fill="x", expand=True, padx=5)

        ttk.Label(color_frame, textvariable=color_var).pack(side="left", padx=5)

        # Line Threshold
        line_frame = ttk.Frame(detection_frame)
        line_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(line_frame, text="Line Threshold:").pack(side="left", padx=5)

        line_var = tk.IntVar(value=self.app.config.get("line_threshold", 200))
        line_scale = ttk.Scale(
            line_frame, from_=150, to=250, orient="horizontal", variable=line_var
        )
        line_scale.pack(side="left", fill="x", expand=True, padx=5)

        ttk.Label(line_frame, textvariable=line_var).pack(side="left", padx=5)

        # กรอบการตั้งค่าสี
        color_settings_frame = ttk.LabelFrame(parent, text="Color Settings")
        color_settings_frame.pack(fill="x", padx=10, pady=10)

        # Green Color
        green_color_frame = ttk.Frame(color_settings_frame)
        green_color_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(green_color_frame, text="Green Color:").pack(side="left", padx=5)

        green_color_var = tk.StringVar(
            value=self.app.config.get("green_color", "rgba(83,250,83,255)")
        )
        green_color_entry = ttk.Entry(
            green_color_frame, textvariable=green_color_var, width=20
        )
        green_color_entry.pack(side="left", padx=5)

        # แสดงตัวอย่างสีเขียว
        green_color_sample = tk.Canvas(
            green_color_frame,
            width=30,
            height=20,
            bg="#53FA53",
            highlightthickness=1,
            highlightbackground="black",
        )
        green_color_sample.pack(side="left", padx=5)

        # Red Color
        red_color_frame = ttk.Frame(color_settings_frame)
        red_color_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(red_color_frame, text="Red Color:").pack(side="left", padx=5)

        red_color_var = tk.StringVar(
            value=self.app.config.get("red_color", "rgba(251,98,76,255)")
        )
        red_color_entry = ttk.Entry(
            red_color_frame, textvariable=red_color_var, width=20
        )
        red_color_entry.pack(side="left", padx=5)

        # แสดงตัวอย่างสีแดง
        red_color_sample = tk.Canvas(
            red_color_frame,
            width=30,
            height=20,
            bg="#FB624C",
            highlightthickness=1,
            highlightbackground="black",
        )
        red_color_sample.pack(side="left", padx=5)

        # White Color
        white_color_frame = ttk.Frame(color_settings_frame)
        white_color_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(white_color_frame, text="White Color:").pack(side="left", padx=5)

        white_color_var = tk.StringVar(
            value=self.app.config.get("white_color", "rgba(255,255,255,255)")
        )
        white_color_entry = ttk.Entry(
            white_color_frame, textvariable=white_color_var, width=20
        )
        white_color_entry.pack(side="left", padx=5)

        # แสดงตัวอย่างสีขาว
        white_color_sample = tk.Canvas(
            white_color_frame,
            width=30,
            height=20,
            bg="#FFFFFF",
            highlightthickness=1,
            highlightbackground="black",
        )
        white_color_sample.pack(side="left", padx=5)

        # ปุ่มตรวจจับสีอัตโนมัติ
        auto_detect_frame = ttk.Frame(color_settings_frame)
        auto_detect_frame.pack(fill="x", padx=5, pady=5)

        ttk.Button(
            auto_detect_frame,
            text="Auto Detect Colors",
            command=self.auto_detect_colors,
        ).pack(side="left", padx=5)

        # สร้างฟังก์ชันเพื่อเก็บการตั้งค่าทั้งหมด
        def get_detection_settings():
            return {
                "green_tolerance": color_var.get(),
                "line_threshold": line_var.get(),
                "green_color": green_color_var.get(),
                "red_color": red_color_var.get(),
                "white_color": white_color_var.get(),
            }

        # เก็บฟังก์ชันไว้ในออบเจ็กต์เพื่อเรียกใช้ภายหลัง
        parent.get_settings = get_detection_settings

    def build_hotkey_settings(self, parent):
        """สร้างการตั้งค่าคีย์ลัด"""
        # กรอบการตั้งค่าคีย์ลัด
        hotkey_frame = ttk.LabelFrame(parent, text="Hotkey Settings")
        hotkey_frame.pack(fill="x", padx=10, pady=10)

        # Start Hotkey
        start_hotkey_frame = ttk.Frame(hotkey_frame)
        start_hotkey_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(start_hotkey_frame, text="Start Hotkey:").pack(side="left", padx=5)

        start_hotkey_var = tk.StringVar(value=self.app.config.get("start_hotkey", "f6"))
        start_hotkey_combo = ttk.Combobox(
            start_hotkey_frame, textvariable=start_hotkey_var, state="readonly"
        )
        start_hotkey_combo["values"] = (
            "f1",
            "f2",
            "f3",
            "f4",
            "f5",
            "f6",
            "f7",
            "f8",
            "f9",
            "f10",
            "f11",
            "f12",
        )
        start_hotkey_combo.pack(side="left", padx=5)

        # Stop Hotkey
        stop_hotkey_frame = ttk.Frame(hotkey_frame)
        stop_hotkey_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(stop_hotkey_frame, text="Stop Hotkey:").pack(side="left", padx=5)

        stop_hotkey_var = tk.StringVar(value=self.app.config.get("stop_hotkey", "f10"))
        stop_hotkey_combo = ttk.Combobox(
            stop_hotkey_frame, textvariable=stop_hotkey_var, state="readonly"
        )
        stop_hotkey_combo["values"] = (
            "f1",
            "f2",
            "f3",
            "f4",
            "f5",
            "f6",
            "f7",
            "f8",
            "f9",
            "f10",
            "f11",
            "f12",
        )
        stop_hotkey_combo.pack(side="left", padx=5)

        # Fishing Key
        fishing_key_frame = ttk.Frame(hotkey_frame)
        fishing_key_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(fishing_key_frame, text="Fishing Key:").pack(side="left", padx=5)

        fishing_key_var = tk.StringVar(value=self.app.config.get("fishing_key", "e"))
        fishing_key_combo = ttk.Combobox(
            fishing_key_frame, textvariable=fishing_key_var, state="readonly"
        )
        fishing_key_combo["values"] = tuple("abcdefghijklmnopqrstuvwxyz0123456789")
        fishing_key_combo.pack(side="left", padx=5)

        # คำอธิบาย
        description_frame = ttk.Frame(parent)
        description_frame.pack(fill="x", padx=10, pady=10)

        description_text = ttk.Label(
            description_frame,
            text="Note: Changes to hotkeys will take effect after restarting the application.",
            font=("Arial", 9),
            foreground=self.theme_manager.warning_color,
            wraplength=400,
        )
        description_text.pack(padx=5, pady=5)

        # สร้างฟังก์ชันเพื่อเก็บการตั้งค่าทั้งหมด
        def get_hotkey_settings():
            return {
                "start_hotkey": start_hotkey_var.get(),
                "stop_hotkey": stop_hotkey_var.get(),
                "fishing_key": fishing_key_var.get(),
            }

        # เก็บฟังก์ชันไว้ในออบเจ็กต์เพื่อเรียกใช้ภายหลัง
        parent.get_settings = get_hotkey_settings

    def build_advanced_settings(self, parent):
        """สร้างการตั้งค่าขั้นสูง"""
        # กรอบการตั้งค่าขั้นสูง
        advanced_frame = ttk.LabelFrame(parent, text="Advanced Settings")
        advanced_frame.pack(fill="x", padx=10, pady=10)

        # Auto Restart
        auto_restart_frame = ttk.Frame(advanced_frame)
        auto_restart_frame.pack(fill="x", padx=5, pady=5)

        auto_restart_var = tk.BooleanVar(
            value=self.app.config.get("auto_restart", False)
        )
        auto_restart_check = ttk.Checkbutton(
            auto_restart_frame,
            text="Auto Restart Fishing (when no line detected)",
            variable=auto_restart_var,
        )
        auto_restart_check.pack(side="left", padx=5)

        # Auto Start
        auto_start_frame = ttk.Frame(advanced_frame)
        auto_start_frame.pack(fill="x", padx=5, pady=5)

        auto_start_var = tk.BooleanVar(value=self.app.config.get("auto_start", False))
        auto_start_check = ttk.Checkbutton(
            auto_start_frame,
            text="Auto Start on Application Launch",
            variable=auto_start_var,
        )
        auto_start_check.pack(side="left", padx=5)

        # Debug Mode
        debug_frame = ttk.Frame(advanced_frame)
        debug_frame.pack(fill="x", padx=5, pady=5)

        debug_var = tk.BooleanVar(value=self.app.config.get("debug_mode", False))
        debug_check = ttk.Checkbutton(
            debug_frame, text="Enable Debug Mode", variable=debug_var
        )
        debug_check.pack(side="left", padx=5)

        # คำเตือน
        warning_frame = ttk.Frame(parent)
        warning_frame.pack(fill="x", padx=10, pady=10)

        warning_text = ttk.Label(
            warning_frame,
            text="Warning: Advanced settings may affect performance or stability. Use with caution.",
            font=("Arial", 9, "bold"),
            foreground=self.theme_manager.warning_color,
            wraplength=400,
        )
        warning_text.pack(padx=5, pady=5)

        # การสำรองข้อมูลและกู้คืน
        backup_frame = ttk.LabelFrame(parent, text="Backup & Restore")
        backup_frame.pack(fill="x", padx=10, pady=10)

        backup_buttons = ttk.Frame(backup_frame)
        backup_buttons.pack(fill="x", padx=5, pady=5)

        ttk.Button(
            backup_buttons, text="Backup Settings", command=self.backup_settings
        ).pack(side="left", padx=5)
        ttk.Button(
            backup_buttons, text="Restore Settings", command=self.restore_settings
        ).pack(side="left", padx=5)

        # สร้างฟังก์ชันเพื่อเก็บการตั้งค่าทั้งหมด
        def get_advanced_settings():
            return {
                "auto_restart": auto_restart_var.get(),
                "auto_start": auto_start_var.get(),
                "debug_mode": debug_var.get(),
            }

        # เก็บฟังก์ชันไว้ในออบเจ็กต์เพื่อเรียกใช้ภายหลัง
        parent.get_settings = get_advanced_settings

    def build_help_tab(self, parent):
        """สร้างแท็บช่วยเหลือ (Help)"""
        # ส่วนหัวข้อ
        help_header = ttk.Frame(parent)
        help_header.pack(fill="x", padx=10, pady=10)

        ttk.Label(
            help_header, text="Fishing Master Pro Help", font=("Arial", 14, "bold")
        ).pack(pady=5)

        # สร้าง Notebook สำหรับแบ่งหมวดหมู่ความช่วยเหลือ
        help_notebook = ttk.Notebook(parent)
        help_notebook.pack(fill="both", expand=True, padx=10, pady=5)

        # สร้างแท็บย่อย
        getting_started_tab = ttk.Frame(help_notebook)
        help_notebook.add(getting_started_tab, text="Getting Started")

        faq_tab = ttk.Frame(help_notebook)
        help_notebook.add(faq_tab, text="FAQ")

        troubleshooting_tab = ttk.Frame(help_notebook)
        help_notebook.add(troubleshooting_tab, text="Troubleshooting")

        about_tab = ttk.Frame(help_notebook)
        help_notebook.add(about_tab, text="About")

        # เนื้อหา Getting Started
        gs_frame = ttk.Frame(getting_started_tab)
        gs_frame.pack(fill="both", expand=True, padx=10, pady=10)

        gs_text = tk.Text(gs_frame, wrap="word", height=20, font=("Arial", 10))
        gs_text.pack(fill="both", expand=True, side="left")

        gs_scroll = ttk.Scrollbar(gs_frame, command=gs_text.yview)
        gs_scroll.pack(fill="y", side="right")

        gs_text.configure(yscrollcommand=gs_scroll.set)

        # เพิ่มเนื้อหา
        gs_content = """
# Getting Started with Fishing Master Pro

## Basic Setup
1. Launch the application
2. Click the 'Select Region' button
3. Click and drag to select the gauge area in your game
4. Click the 'Start' button to begin automatic fishing

## Understanding the Interface
- The main tab shows your fishing status and controls
- The Statistics tab tracks your fishing performance
- The Settings tab allows you to customize the application
- Use hotkeys F6 to start and F10 to stop fishing at any time

## Tips for Optimal Performance
- Select a region that contains only the fishing gauge
- Adjust the color sensitivity if detection is inconsistent
- Use a stable internet connection for best results
- Run games in windowed mode for better integration
        """

        gs_text.insert("1.0", gs_content)
        gs_text.configure(state="disabled")

        # เนื้อหา FAQ
        faq_frame = ttk.Frame(faq_tab)
        faq_frame.pack(fill="both", expand=True, padx=10, pady=10)

        faq_text = tk.Text(faq_frame, wrap="word", height=20, font=("Arial", 10))
        faq_text.pack(fill="both", expand=True, side="left")

        faq_scroll = ttk.Scrollbar(faq_frame, command=faq_text.yview)
        faq_scroll.pack(fill="y", side="right")

        faq_text.configure(yscrollcommand=faq_scroll.set)

        # เพิ่มเนื้อหา
        faq_content = """
# Frequently Asked Questions

## Q: Will this work with any fishing game?
A: The app is designed to work with games that have a visual fishing gauge with a moving indicator. It works best with games that have clear color distinctions.

## Q: Is it safe to use?
A: The app only captures screenshots and simulates mouse clicks. It doesn't modify any game files or memory.

## Q: Why is detection not working?
A: Try adjusting the color sensitivity and line threshold in Settings. Also ensure the selected region properly contains the gauge.

## Q: Can I get banned for using this?
A: While we don't modify game files, some games prohibit automation tools. Use at your own discretion.

## Q: How do I customize the colors?
A: Go to Settings > Detection and adjust the RGB values for green, red, and white colors.

## Q: Can I set different hotkeys?
A: Yes, go to Settings > Hotkeys to customize your keyboard shortcuts.
        """

        faq_text.insert("1.0", faq_content)
        faq_text.configure(state="disabled")

        # เนื้อหา Troubleshooting
        ts_frame = ttk.Frame(troubleshooting_tab)
        ts_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ts_text = tk.Text(ts_frame, wrap="word", height=20, font=("Arial", 10))
        ts_text.pack(fill="both", expand=True, side="left")

        ts_scroll = ttk.Scrollbar(ts_frame, command=ts_text.yview)
        ts_scroll.pack(fill="y", side="right")

        ts_text.configure(yscrollcommand=ts_scroll.set)

        # เพิ่มเนื้อหา
        ts_content = """
# Troubleshooting Guide

## No Detection
- Make sure your game window is visible and not minimized
- Verify the selected region contains the fishing gauge
- Try adjusting the color sensitivity and line threshold
- Check if the colors in Settings match your game's colors

## Application Crashes
- Ensure you have the latest version of the application
- Check if your system meets the minimum requirements
- Try running the application as administrator
- Disable other screen capture or overlay software

## High CPU Usage
- Reduce the animation speed in Settings
- Close other applications while fishing
- Reduce your game's graphics settings
- Consider upgrading your hardware if issues persist

## Clicking Issues
- Make sure your game window is focused
- Try adjusting the action cooldown settings
- Test if manual clicking works in the same area
- Check if any other software is blocking input

## Other Issues
- Restart the application and try again
- Check for updates on our website
- Reset to default settings and reconfigure
        """

        ts_text.insert("1.0", ts_content)
        ts_text.configure(state="disabled")

        # เนื้อหา About
        about_frame = ttk.Frame(about_tab)
        about_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # โลโก้
        try:
            logo_path = os.path.join("assets", "icons", "logo.png")
            if os.path.exists(logo_path):
                # โหลดและปรับขนาดรูปภาพ
                logo_img = Image.open(logo_path)
                logo_img = logo_img.resize((150, 150), Image.LANCZOS)
                logo_photo = ImageTk.PhotoImage(logo_img)

                logo_label = ttk.Label(about_frame, image=logo_photo)
                logo_label.image = logo_photo  # เก็บอ้างอิงเพื่อป้องกัน garbage collection
                logo_label.pack(pady=10)
        except Exception:
            # ถ้าไม่มีไฟล์รูปภาพ ให้ใช้ข้อความแทน
            pass

        # ข้อความแนะนำ
        about_content = ttk.Label(
            about_frame,
            text="Fishing Master Pro v1.0.0\n\n"
            "An intelligent fishing assistant for gamers\n"
            "© 2025 All rights reserved.\n\n"
            "Developed by AI Team\n\n"
            "Contact: support@fishingmasterpro.com",
            justify=tk.CENTER,
            font=("Arial", 10),
        )
        about_content.pack(pady=10)

        # ปุ่ม
        button_frame = ttk.Frame(about_frame)
        button_frame.pack(pady=10)

        ttk.Button(
            button_frame, text="Check for Updates", command=self.check_for_updates
        ).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Visit Website", command=self.visit_website).pack(
            side="left", padx=5
        )

    # ฟังก์ชันการทำงานต่างๆ
    def toggle_theme(self):
        """สลับธีมระหว่างสว่างและมืด"""
        current_theme = self.theme_manager.current_theme
        if current_theme == "light":
            self.theme_manager.set_theme("dark")
        else:
            self.theme_manager.set_theme("light")

    def update_status(self, text, status_type="primary"):
        """อัปเดตสถานะในหน้า UI หลัก"""
        # กำหนดสีตามประเภทสถานะ
        color_map = {
            "primary": self.theme_manager.primary_color,
            "success": self.theme_manager.secondary_color,
            "danger": self.theme_manager.warning_color,
            "warning": "#f39c12",  # สีส้ม
            "inactive": "#7f8c8d",  # สีเทา
        }

        color = color_map.get(status_type, self.theme_manager.primary_color)

        # อัปเดตตัวบ่งชี้สถานะและข้อความ
        if self.status_indicator and self.status_text:
            self.status_canvas.itemconfig(self.status_indicator, fill=color)
            self.status_canvas.itemconfig(
                self.status_text, text=text, fill=self.theme_manager.text_color
            )

        # อัปเดตสถานะในตัวจำลองเกจ
        if self.gauge_visualizer:
            self.gauge_visualizer.update_status(text)

    def update_region_info(self, region):
        """อัปเดตข้อมูลพื้นที่ที่เลือก"""
        if region and self.region_label:
            x1, y1, x2, y2 = region
            self.region_label.config(text=f"({x1}, {y1}) to ({x2}, {y2})")

    def update_line_position(self, relative_pos):
        """อัปเดตตำแหน่งเส้นในตัวจำลองเกจ"""
        if self.gauge_visualizer:
            self.gauge_visualizer.update_line_position(relative_pos)

    def update_catch_counter(self, count):
        """อัปเดตตัวนับจำนวนปลาที่จับได้"""
        self.catch_counter.set(str(count))

    def update_detection_rate(self, rate):
        """อัปเดตอัตราการตรวจจับ"""
        self.detection_rate.set(f"{rate}%")

    def update_sample_image(self, image):
        """อัปเดตภาพตัวอย่าง"""
        try:
            # แปลงภาพ OpenCV (BGR) เป็น RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # คำนวณขนาดที่เหมาะสม
            height, width = image_rgb.shape[:2]
            canvas_width = self.sample_canvas.winfo_width()

            if canvas_width <= 1:  # ถ้ายังไม่ได้แสดงผล
                canvas_width = 400  # ค่าเริ่มต้น

            # คำนวณอัตราส่วน
            ratio = min(canvas_width / width, 120 / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)

            # ปรับขนาดภาพ
            image_resized = cv2.resize(image_rgb, (new_width, new_height))

            # แปลงเป็น PIL Image
            pil_image = Image.fromarray(image_resized)

            # แปลงเป็น PhotoImage สำหรับ Tkinter
            self.sample_photo = ImageTk.PhotoImage(pil_image)

            # ลบข้อความคำแนะนำ
            self.sample_canvas.delete("all")

            # ปรับขนาด canvas
            self.sample_canvas.config(height=new_height)

            # แสดงภาพ
            self.sample_canvas.create_image(
                canvas_width // 2, new_height // 2, image=self.sample_photo
            )
        except Exception as e:
            print(f"Error updating sample image: {e}")

    def set_button_states(self, select=True, start=False, stop=False):
        """ตั้งค่าสถานะของปุ่มต่างๆ"""
        self.select_button.config(state="normal" if select else "disabled")
        self.start_button.config(state="normal" if start else "disabled")
        self.stop_button.config(state="normal" if stop else "disabled")

    def reset_counter(self):
        """รีเซ็ตตัวนับจำนวนปลาที่จับได้"""
        self.catch_counter.set("0")
        # ถ้ามีการรีเซ็ตขณะกำลังทำงานอยู่
        if self.app.running:
            # รีเซ็ตตัวนับในเซสชันปัจจุบัน
            self.app.analytics.current_session["catches"] = 0

    ### modules/ui/modern_ui.py (continued)
    def export_statistics(self):
        """ส่งออกสถิติเป็นไฟล์ CSV"""
        try:
            import csv
            from tkinter import filedialog
            from datetime import datetime

            # เวลาปัจจุบัน
            now = datetime.now().strftime("%Y%m%d_%H%M%S")

            # เลือกตำแหน่งบันทึกไฟล์
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialfile=f"fishing_stats_{now}.csv",
            )

            if not file_path:
                return

            # โหลดสถิติ
            stats = self.app.analytics.get_all_time_stats()

            # เขียนไฟล์ CSV
            with open(file_path, "w", newline="") as file:
                writer = csv.writer(file)

                # หัวข้อ
                writer.writerow(["Fishing Statistics Export", f"Generated on {now}"])
                writer.writerow([])

                # สถิติโดยรวม
                writer.writerow(["All-time Statistics"])
                writer.writerow(["Total Catches", stats["total_catches"]])
                writer.writerow(["Total Sessions", stats["total_sessions"]])
                writer.writerow(
                    ["Total Time (hours)", f"{stats['total_time']/3600:.2f}"]
                )
                writer.writerow(["Total Clicks", stats["total_clicks"]])
                writer.writerow([])

                # เซสชันที่ดีที่สุด
                writer.writerow(["Best Session"])
                writer.writerow(["Date", stats["best_session"]["date"]])
                writer.writerow(["Catches", stats["best_session"]["catches"]])
                writer.writerow(
                    [
                        "Duration (hours)",
                        f"{stats['best_session']['duration']/3600:.2f}",
                    ]
                )
                writer.writerow([])

                # ประวัติเซสชัน
                writer.writerow(["Session History"])
                writer.writerow(
                    [
                        "Date",
                        "Catches",
                        "Duration (hours)",
                        "Clicks",
                        "Catch Rate (fish/h)",
                    ]
                )

                for session in stats["history"]:
                    rate = 0
                    if session["duration"] > 0:
                        rate = (session["catches"] / session["duration"]) * 3600

                    writer.writerow(
                        [
                            session["date"],
                            session["catches"],
                            f"{session['duration']/3600:.2f}",
                            session.get("clicks", 0),
                            f"{rate:.2f}",
                        ]
                    )

            self.show_notification("Statistics exported successfully", "success")
        except Exception as e:
            self.show_notification(f"Error exporting statistics: {e}", "error")

    def reset_all_statistics(self):
        """รีเซ็ตสถิติทั้งหมด"""
        # ขอคำยืนยัน
        confirm = messagebox.askyesno(
            "Reset All Statistics",
            "Are you sure you want to reset all statistics? This action cannot be undone.",
        )

        if confirm:
            # รีเซ็ตสถิติ
            self.app.analytics.stats = self.app.analytics.load_statistics()
            self.app.analytics.save_statistics()

            # รีเซ็ตการแสดงผล
            self.catch_counter.set("0")

            # อัปเดตแท็บสถิติ
            self.tab_panel.rebuild_tab(1)  # สร้างแท็บสถิติใหม่

            self.show_notification("All statistics have been reset", "success")

    def reset_to_default_settings(self):
        """รีเซ็ตการตั้งค่าเป็นค่าเริ่มต้น"""
        # ขอคำยืนยัน
        confirm = messagebox.askyesno(
            "Reset to Default",
            "Are you sure you want to reset all settings to default? This will not affect your statistics.",
        )

        if confirm:
            # โหลดการตั้งค่าเริ่มต้น
            self.app.config = self.app.config_manager.default_config.copy()

            # บันทึกการตั้งค่า
            self.app.config_manager.save_config(self.app.config)

            # อัปเดตการตั้งค่าให้ detector
            self.app.detector.update_settings_from_config(self.app.config)

            # สร้าง UI ใหม่
            for i in range(2, 4):  # สร้างแท็บการตั้งค่าและขั้นสูงใหม่
                self.tab_panel.rebuild_tab(i)

            # อัปเดตธีม
            self.theme_manager.set_theme(self.app.config["theme"])

            self.show_notification("Settings reset to default", "success")

    def backup_settings(self):
        """สำรองการตั้งค่าลงไฟล์"""
        try:
            from tkinter import filedialog
            from datetime import datetime
            import json
            import shutil

            # เวลาปัจจุบัน
            now = datetime.now().strftime("%Y%m%d_%H%M%S")

            # เลือกตำแหน่งบันทึกไฟล์
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json")],
                initialfile=f"fishing_settings_backup_{now}.json",
            )

            if not file_path:
                return

            # บันทึกการตั้งค่าปัจจุบัน
            self.app.save_settings()

            # คัดลอกไฟล์การตั้งค่า
            shutil.copy2(self.app.config_manager.config_file, file_path)

            self.show_notification("Settings backed up successfully", "success")
        except Exception as e:
            self.show_notification(f"Error backing up settings: {e}", "error")

    def restore_settings(self):
        """กู้คืนการตั้งค่าจากไฟล์"""
        try:
            from tkinter import filedialog
            import json
            import shutil

            # เลือกไฟล์
            file_path = filedialog.askopenfilename(
                defaultextension=".json", filetypes=[("JSON files", "*.json")]
            )

            if not file_path:
                return

            # ขอคำยืนยัน
            confirm = messagebox.askyesno(
                "Restore Settings",
                "Are you sure you want to restore settings from this file? Current settings will be overwritten.",
            )

            if not confirm:
                return

            # คัดลอกไฟล์ที่เลือกมาเป็นไฟล์การตั้งค่า
            shutil.copy2(file_path, self.app.config_manager.config_file)

            # โหลดการตั้งค่าใหม่
            self.app.config = self.app.config_manager.load_config()

            # อัปเดตการตั้งค่าให้ detector
            self.app.detector.update_settings_from_config(self.app.config)

            # สร้าง UI ใหม่
            for i in range(2, 4):  # สร้างแท็บการตั้งค่าและขั้นสูงใหม่
                self.tab_panel.rebuild_tab(i)

            # อัปเดตธีม
            self.theme_manager.set_theme(self.app.config["theme"])

            self.show_notification("Settings restored successfully", "success")
        except Exception as e:
            self.show_notification(f"Error restoring settings: {e}", "error")

    def auto_detect_colors(self):
        """ตรวจจับสีอัตโนมัติจากภาพตัวอย่าง"""
        if not self.app.detector.detected_area_image is not None:
            self.show_notification(
                "No sample image available. Please select a region first.", "warning"
            )
            return

        try:
            # สร้างการแสดงตัวอย่างการตรวจจับสี
            self.create_color_detection_preview()
        except Exception as e:
            self.show_notification(f"Error detecting colors: {e}", "error")

    def create_color_detection_preview(self):
        """สร้างหน้าต่างแสดงตัวอย่างการตรวจจับสี"""
        # สร้างหน้าต่างใหม่
        preview_win = tk.Toplevel(self.root)
        preview_win.title("Color Detection Preview")
        preview_win.geometry("600x400")
        preview_win.resizable(False, False)

        # โหลดภาพตัวอย่าง
        image = self.app.detector.detected_area_image.copy()

        # แปลงเป็น RGB และปรับขนาด
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width = image_rgb.shape[:2]

        # คำนวณอัตราส่วน
        ratio = min(500 / width, 250 / height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)

        # ปรับขนาดภาพ
        image_resized = cv2.resize(image_rgb, (new_width, new_height))

        # แปลงเป็น PIL Image
        pil_image = Image.fromarray(image_resized)

        # แปลงเป็น PhotoImage
        photo = ImageTk.PhotoImage(pil_image)

        # สร้าง canvas สำหรับแสดงภาพ
        canvas = tk.Canvas(preview_win, width=new_width, height=new_height)
        canvas.pack(pady=10)

        # แสดงภาพ
        canvas.create_image(0, 0, anchor="nw", image=photo)
        canvas.image = photo  # เก็บอ้างอิงเพื่อป้องกัน garbage collection

        # สร้างกรอบควบคุม
        control_frame = ttk.Frame(preview_win)
        control_frame.pack(fill="x", padx=10, pady=10)

        # ตัวแปรสำหรับเก็บสีที่ตรวจจับได้
        detected_green = tk.StringVar()
        detected_red = tk.StringVar()
        detected_white = tk.StringVar()

        # สร้างปุ่มตรวจจับสีแต่ละประเภท
        ttk.Button(
            control_frame,
            text="Detect Green",
            command=lambda: self.detect_color_from_image(
                image, "green", detected_green
            ),
        ).grid(row=0, column=0, padx=5, pady=5)

        ttk.Entry(control_frame, textvariable=detected_green, width=20).grid(
            row=0, column=1, padx=5, pady=5
        )

        ttk.Button(
            control_frame,
            text="Detect Red",
            command=lambda: self.detect_color_from_image(image, "red", detected_red),
        ).grid(row=1, column=0, padx=5, pady=5)

        ttk.Entry(control_frame, textvariable=detected_red, width=20).grid(
            row=1, column=1, padx=5, pady=5
        )

        ttk.Button(
            control_frame,
            text="Detect White",
            command=lambda: self.detect_color_from_image(
                image, "white", detected_white
            ),
        ).grid(row=2, column=0, padx=5, pady=5)

        ttk.Entry(control_frame, textvariable=detected_white, width=20).grid(
            row=2, column=1, padx=5, pady=5
        )

        # ปุ่มบันทึกค่าสีที่ตรวจจับได้
        ttk.Button(
            preview_win,
            text="Save Detected Colors",
            command=lambda: self.save_detected_colors(
                detected_green.get(),
                detected_red.get(),
                detected_white.get(),
                preview_win,
            ),
        ).pack(pady=10)

        # คำแนะนำ
        instruction = ttk.Label(
            preview_win,
            text="Click each button to detect the corresponding color from the image.",
            font=("Arial", 9),
            wraplength=500,
        )
        instruction.pack(pady=5)

    def detect_color_from_image(self, image, color_type, result_var):
        """ตรวจจับสีจากภาพตัวอย่าง"""
        try:
            # ทำ color segmentation
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

            if color_type == "green":
                # ตรวจจับสีเขียว
                lower_green = np.array([40, 50, 50])
                upper_green = np.array([80, 255, 255])
                mask = cv2.inRange(hsv, lower_green, upper_green)
            elif color_type == "red":
                # ตรวจจับสีแดง (โทนแดงมี 2 ช่วงใน HSV)
                lower_red1 = np.array([0, 50, 50])
                upper_red1 = np.array([10, 255, 255])
                lower_red2 = np.array([170, 50, 50])
                upper_red2 = np.array([180, 255, 255])
                mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
                mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
                mask = mask1 + mask2
            else:  # white
                # ตรวจจับสีขาว
                lower_white = np.array([0, 0, 200])
                upper_white = np.array([180, 30, 255])
                mask = cv2.inRange(hsv, lower_white, upper_white)

            # หาพิกัดของจุดที่มีสีตามที่ต้องการ
            coords = cv2.findNonZero(mask)

            if coords is not None and len(coords) > 0:
                # หาค่าเฉลี่ยของสีในพื้นที่ที่มีสีตามที่ต้องการ
                mean_color = cv2.mean(image, mask=mask)[:3]

                # แปลงเป็นรูปแบบ RGBA
                r, g, b = int(mean_color[2]), int(mean_color[1]), int(mean_color[0])
                rgba_str = f"rgba({r},{g},{b},255)"

                # อัปเดตตัวแปรผลลัพธ์
                result_var.set(rgba_str)

                return rgba_str
            else:
                result_var.set("No color detected")
                return None
        except Exception as e:
            print(f"Error detecting color: {e}")
            result_var.set("Error")
            return None

    def save_detected_colors(self, green, red, white, window):
        """บันทึกสีที่ตรวจจับได้ลงการตั้งค่า"""
        valid = True

        # ตรวจสอบว่าค่าสีทั้งหมดถูกต้อง
        for color in [green, red, white]:
            if not color or color in ["No color detected", "Error"]:
                valid = False
                break

        if not valid:
            messagebox.showerror(
                "Invalid Colors",
                "Some colors were not properly detected. Please try again.",
            )
            return

        # อัปเดตการตั้งค่า
        self.app.config["green_color"] = green
        self.app.config["red_color"] = red
        self.app.config["white_color"] = white

        # อัปเดตการตั้งค่าให้ detector
        self.app.detector.update_settings_from_config(self.app.config)

        # ปิดหน้าต่าง
        window.destroy()

        # แสดงแจ้งเตือน
        self.show_notification("Colors updated successfully", "success")

        # อัปเดตแท็บการตั้งค่า
        self.tab_panel.rebuild_tab(2)  # สร้างแท็บการตั้งค่าใหม่

    def check_for_updates(self):
        """ตรวจสอบอัปเดต (จำลอง)"""
        self.show_notification("You are using the latest version (1.0.0)", "success")

    def visit_website(self):
        """เปิดเว็บไซต์ (จำลอง)"""
        messagebox.showinfo(
            "Website",
            "This would normally open the Fishing Master Pro website in your browser.",
        )

    def get_all_settings(self):
        """รวบรวมการตั้งค่าทั้งหมดจากแท็บต่างๆ"""
        settings = {}

        # ดึงการตั้งค่าจากแต่ละแท็บ
        for i in range(2, 4):  # แท็บการตั้งค่า (2) และขั้นสูง (3)
            tab = self.tab_panel.get_tab(i)
            if hasattr(tab, "get_settings"):
                settings.update(tab.get_settings())

        return settings

    def show_notification(self, message, notification_type="info", duration=3000):
        """แสดงการแจ้งเตือนในหน้าต่างโปรแกรม"""
        # สร้าง notification
        notification = Notification(
            self.root, message, notification_type, duration, self.theme_manager
        )

    def start_animations(self):
        """เริ่มต้นอนิเมชันทั้งหมด"""
        self.update_session_time()

    def update_session_time(self):
        """อัปเดตเวลาเซสชันที่แสดงใน UI"""
        if self.app.running:
            # คำนวณเวลาที่ผ่านไป
            session_stats = self.app.analytics.get_current_session_stats()
            seconds = int(session_stats["duration"])

            # แปลงเป็นรูปแบบ HH:MM:SS
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60

            time_str = f"{hours:02d}:{minutes:02d}:{secs:02d}"
            self.session_time.set(time_str)

            # อัปเดตอัตราการจับ
            if seconds > 0:
                rate = session_stats["catch_rate"]
                self.catch_rate.set(f"{rate:.1f}/h")

        # เรียกตัวเองทุก 1 วินาที
        self.root.after(1000, self.update_session_time)
