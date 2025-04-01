import tkinter as tk
from tkinter import ttk
import time
import threading
import random
import math

from ui.gauge_widget import PixelGauge
from utils.constants import PIXEL_COLORS, UI_CONSTANTS, TIPS


class PixelatedUI:
    def __init__(self, root, app):
        self.root = root
        self.app = app

        # Set window to always on top
        self.root.attributes("-topmost", True)

        # ใช้ค่าสีจาก constants
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

        # Position tracking
        self.last_position = 0.5

        # Configure the root window for pixel art style
        self.root.configure(bg=self.bg_color)
        self.root.option_add(
            "*Font", f"{UI_CONSTANTS['FONT_FAMILY']} 10"
        )  # Pixel-like font

        # Add window title and icon (if available)
        self.root.title("Retro Fishing Bot")
        try:
            self.root.iconbitmap("fish_icon.ico")  # Add an icon if available
        except:
            pass  # No icon available

        # Create UI components
        self.create_ui()

        # Start animation for the gauge
        self.start_animation()

    def create_ui(self):
        """Create pixel art styled UI with retro CRT effects"""
        # Configure style for widgets
        style = ttk.Style()
        style.theme_use("default")

        # Configure button styles with pixel-like appearance
        style.configure(
            "Pixel.TButton",
            font=(UI_CONSTANTS["FONT_FAMILY"], 10, "bold"),
            background=self.primary_color,
            foreground=self.text_color,
            borderwidth=2,
            relief="raised",
        )

        style.configure(
            "PixelSuccess.TButton",
            font=(UI_CONSTANTS["FONT_FAMILY"], 10, "bold"),
            background=self.success_color,
            foreground=self.text_color,
            borderwidth=2,
            relief="raised",
        )

        style.configure(
            "PixelDanger.TButton",
            font=(UI_CONSTANTS["FONT_FAMILY"], 10, "bold"),
            background=self.danger_color,
            foreground=self.text_color,
            borderwidth=2,
            relief="raised",
        )

        # Configure frames, labels and other widgets
        style.configure("Pixel.TFrame", background=self.bg_color)
        style.configure(
            "PixelPanel.TFrame",
            background=self.panel_bg,
            borderwidth=2,
            relief="raised",
        )
        style.configure(
            "Pixel.TLabel",
            background=self.bg_color,
            foreground=self.text_color,
            font=(UI_CONSTANTS["FONT_FAMILY"], 10),
        )
        style.configure(
            "PixelTitle.TLabel",
            background=self.bg_color,
            foreground=self.accent_color,
            font=(UI_CONSTANTS["FONT_FAMILY"], 12, "bold"),
        )
        style.configure(
            "Pixel.TLabelframe",
            background=self.panel_bg,
            foreground=self.accent_color,
            borderwidth=2,
            relief="raised",
        )
        style.configure(
            "Pixel.TLabelframe.Label",
            background=self.panel_bg,
            foreground=self.accent_color,
            font=(UI_CONSTANTS["FONT_FAMILY"], 10, "bold"),
        )

        # Main frame
        main_frame = ttk.Frame(
            self.root, style="Pixel.TFrame", padding=UI_CONSTANTS["PADDING"]
        )
        main_frame.pack(fill="both", expand=True)

        # Header section with pixelated title and character
        header_frame = ttk.Frame(main_frame, style="PixelPanel.TFrame")
        header_frame.pack(fill="x", pady=(0, 15), ipady=5)

        # Add pixel character
        character_frame = tk.Frame(header_frame, bg=self.panel_bg)
        character_frame.pack(pady=(10, 5))

        # Title with retro font
        title_label = tk.Label(
            header_frame,
            text="╔═════════════════════════╗\n"
            "║  RETRO FISHING MASTER   ║\n"
            "╚═════════════════════════╝",
            font=(UI_CONSTANTS["FONT_FAMILY"], 14, "bold"),
            fg=self.crt_color,
            bg=self.panel_bg,
            justify="center",
        )
        title_label.pack(pady=(0, 10))

        # Instruction text with pixel border
        tip_frame = ttk.Frame(main_frame, style="Pixel.TFrame")
        tip_frame.pack(fill="x", pady=5)

        # Create pixel border around tip
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

        # Status frame with pixelated border
        status_frame = ttk.LabelFrame(
            main_frame, text="STATUS", style="Pixel.TLabelframe", padding=10
        )
        status_frame.pack(fill="x", pady=10)

        # Status columns
        status_columns = ttk.Frame(status_frame, style="Pixel.TFrame")
        status_columns.pack(fill="x")

        # Left column - Status
        left_status = ttk.Frame(status_columns, style="Pixel.TFrame")
        left_status.pack(side="top", fill="x", expand=True)

        status_label_title = ttk.Label(
            left_status, text="█ STATUS:", style="Pixel.TLabel"
        )
        status_label_title.pack(side="left", padx=5)

        self.status_label = ttk.Label(left_status, text="READY", style="Pixel.TLabel")
        self.status_label.pack(side="left", padx=5)

        # Right column - Region
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

        # Progress bar with pixel styling
        self.progress_var = tk.DoubleVar()

        # Custom progress bar frame
        progress_frame = ttk.Frame(status_frame, style="Pixel.TFrame")
        progress_frame.pack(fill="x", pady=(10, 0))

        # Create a canvas for custom progress bar
        self.progress_canvas = tk.Canvas(
            progress_frame, height=15, bg=self.bg_color, highlightthickness=0
        )
        self.progress_canvas.pack(fill="x")

        # Initialize custom progress bar
        self.progress_blocks = []
        self.create_pixel_progress_bar()

        # Control section
        control_frame = ttk.LabelFrame(
            main_frame, text="CONTROLS", style="Pixel.TLabelframe", padding=10
        )
        control_frame.pack(fill="x", pady=10)

        button_frame = ttk.Frame(control_frame, style="Pixel.TFrame")
        button_frame.pack(fill="x", pady=5)

        # Configure columns
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)

        # Pixel-styled buttons
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

        # Gauge frame
        gauge_frame = ttk.LabelFrame(
            main_frame, text="GAUGE", style="Pixel.TLabelframe", padding=10
        )
        gauge_frame.pack(fill="x", pady=10)

        # Initialize the gauge widget
        gauge_colors = {
            "success": self.success_color,
            "danger": self.danger_color,
            "warning": self.warning_color,
            "bg": self.bg_color,
            "accent": self.accent_color,
            "crt": self.crt_color,
        }

        # Create the PixelGauge instance
        self.gauge = PixelGauge(gauge_frame, gauge_colors)

        # Indicator data frame
        indicator_frame = ttk.Frame(gauge_frame, style="Pixel.TFrame")
        indicator_frame.pack(fill="x")

        # Split into 2 columns
        indicator_frame.columnconfigure(0, weight=1)
        indicator_frame.columnconfigure(1, weight=1)

        # Left info - Position
        left_info = ttk.Frame(indicator_frame, style="Pixel.TFrame")
        left_info.grid(row=0, column=0, sticky="w")

        position_label = ttk.Label(left_info, text="POSITION:", style="Pixel.TLabel")
        position_label.pack(side="left", padx=2)

        self.position_value = ttk.Label(left_info, text="CENTER", style="Pixel.TLabel")
        self.position_value.pack(side="left", padx=2)

        # Right info - Zone
        right_info = ttk.Frame(indicator_frame, style="Pixel.TFrame")
        right_info.grid(row=0, column=1, sticky="e")

        zone_label = ttk.Label(right_info, text="ZONE:", style="Pixel.TLabel")
        zone_label.pack(side="left", padx=2)

        self.zone_value = ttk.Label(
            right_info, text="SAFE", foreground=self.success_color
        )
        self.zone_value.pack(side="left", padx=2)

        # Footer with hotkey info
        footer_frame = ttk.Frame(main_frame, style="Pixel.TFrame")
        footer_frame.pack(fill="x", pady=(10, 0))

        # Pixelated hotkey indicator
        hotkey_label = tk.Label(
            text="╔═════════════════════════════╗\n"
            f"║  {TIPS['HOTKEY_INFO']}  ║\n"
            "╚═════════════════════════════╝",
            foreground=self.danger_color,
            background=self.bg_color,
            font=(UI_CONSTANTS["FONT_FAMILY"], 10, "bold"),
        )
        hotkey_label.pack(pady=5)

        # Version with pixel decoration
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

    def create_pixel_progress_bar(self):
        """Create a pixelated progress bar"""
        width = self.progress_canvas.winfo_width()
        if width < 10:
            width = 380

        # Clear existing blocks
        for block in self.progress_blocks:
            self.progress_canvas.delete(block)
        self.progress_blocks = []

        # สร้างกรอบรอบแถบความคืบหน้า
        self.progress_canvas.create_rectangle(
            0, 0, width, 15, outline=self.crt_color, width=1
        )

        # Create new blocks with better pixel styling
        block_width = 10
        num_blocks = width // block_width - 1
        padding = 2

        # กำหนดจำนวนแถวของบล็อก
        rows = 3
        block_height = (15 - 2 * padding) / rows

        for i in range(num_blocks):
            for r in range(rows):
                x1 = i * block_width + padding
                y1 = padding + r * block_height
                x2 = (i + 1) * block_width - padding
                y2 = padding + (r + 1) * block_height - 1

                # สร้างบล็อกแบบพิกเซล 8-bit
                block = self.progress_canvas.create_rectangle(
                    x1, y1, x2, y2, fill=self.bg_color, outline=self.panel_bg, width=1
                )
                self.progress_blocks.append(block)

    def update_progress_bar(self, value):
        """Update the pixelated progress bar with animation effects"""
        if not self.progress_blocks:
            return

        num_blocks = len(self.progress_blocks)
        active_blocks = int((value / 100) * num_blocks)

        # กำหนดสีตามค่า
        if value < 30:
            color = self.danger_color
        elif value < 70:
            color = self.warning_color
        else:
            color = self.crt_color

        # อัปเดตสีของบล็อก
        for i, block in enumerate(self.progress_blocks):
            if i < active_blocks:
                # แก้ไขตรงนี้: ทำให้แน่ใจว่าค่าสีที่สร้างขึ้นมีเพียง 6 หลัก
                intensity = 0.8 + (hash((i, int(time.time() * 5) % 10)) % 30) / 100

                # อ่านค่าสีในรูปแบบ hex
                if len(color) == 7:  # สีปกติในรูปแบบ #RRGGBB
                    r = int(color[1:3], 16)
                    g = int(color[3:5], 16)
                    b = int(color[5:7], 16)
                else:
                    # กรณีสีมีรูปแบบอื่น ให้ใช้สีเดิม
                    self.progress_canvas.itemconfig(block, fill=color)
                    continue

                # ปรับความเข้มและสร้างสีใหม่
                r = min(255, int(r * intensity))
                g = min(255, int(g * intensity))
                b = min(255, int(b * intensity))

                # สร้างสีใหม่ในรูปแบบ #RRGGBB
                block_color = f"#{r:02x}{g:02x}{b:02x}"

                # ตรวจสอบเพื่อความแน่ใจ
                if len(block_color) != 7:
                    block_color = color  # ใช้สีเดิมหากสีใหม่ไม่ถูกต้อง

                self.progress_canvas.itemconfig(block, fill=block_color)
            else:
                self.progress_canvas.itemconfig(block, fill=self.bg_color)

    def update_line_position(self, relative_pos):
        """อัปเดตตำแหน่งเส้นตัวชี้ในเกจ"""
        # ใช้ gauge widget แทนโค้ดเก่า
        zone_type, position_text = self.gauge.update_position(relative_pos)

        # อัปเดตข้อความตำแหน่ง
        self.position_value.config(text=position_text)

        # อัปเดตข้อความโซน
        if zone_type == "danger":
            self.zone_value.config(text="DANGER", foreground=self.danger_color)
        elif zone_type == "warning":
            self.zone_value.config(text="CAUTION", foreground=self.warning_color)
        else:
            self.zone_value.config(text="SAFE", foreground=self.success_color)

        # Calculate speed (for visual effects only)
        if hasattr(self, "last_position"):
            speed = abs(relative_pos - self.last_position) * 100 / 0.05
            self.last_position = relative_pos

    def update_status(self, text, status_type="normal"):
        """Update status message with animation effect"""
        self.status_label.config(text=text.upper())

        if status_type == "success":
            self.status_label.config(foreground=self.success_color)
            self.update_progress_bar(100)

        elif status_type == "danger":
            self.status_label.config(foreground=self.danger_color)
            self.update_progress_bar(0)

        elif status_type == "warning":
            self.status_label.config(foreground=self.warning_color)
            # อนิเมชั่นความคืบหน้าที่ไม่แน่นอน
            self.start_progress_animation()
        else:
            self.status_label.config(foreground=self.text_color)
            self.update_progress_bar(50)

    def start_progress_animation(self):
        """Start progress bar animation with indeterminate style"""
        self.blink_counter = 0
        if (
            not hasattr(self, "progress_animation_active")
            or not self.progress_animation_active
        ):
            self.progress_animation_active = True
            self.animate_progress()

    def animate_progress(self):
        """Animate progress bar for indeterminate state"""
        if (
            not hasattr(self, "progress_animation_active")
            or not self.progress_animation_active
        ):
            return

        # สร้างรูปแบบเคลื่อนไหวคล้ายการโหลด
        self.blink_counter = (self.blink_counter + 5) % 100
        self.update_progress_bar(self.blink_counter)

        # ดำเนินการต่อไปหากยังในสถานะ warning
        self.root.after(100, self.animate_progress)

    def stop_progress_animation(self):
        """Stop the progress animation"""
        self.progress_animation_active = False
        self.update_progress_bar(0)

    def update_region_info(self, region):
        """Update selected region information with animation effect"""
        if region:
            x1, y1, x2, y2 = region
            size = f"{x2-x1}x{y2-y1}"
            self.region_label.config(text=f"({x1},{y1})-({x2},{y2}) [{size}]")

            # แสดงข้อความแจ้งเตือนแบบพิกเซล
            self.show_tooltip(f"REGION SELECTED: {size}")

            # อนิเมชันแสดงความสำเร็จในการเลือกพื้นที่
            self.update_progress_bar(100)
            self.root.after(1000, lambda: self.update_progress_bar(50))

    def set_start_button_state(self, state):
        """Set start button state with visual feedback"""
        print(f"Setting start button state to: {state}")

        # แก้ไขเป็นการตั้งค่าโดยตรงก่อน แล้วค่อยทำเอฟเฟกต์
        self.start_button.config(state=state)

        # จากนั้นจึงทำเอฟเฟกต์ (ถ้าจำเป็น)
        if state == "normal" and self.start_button.cget("state") != "disabled":
            self.blink_button(self.start_button, 3)

    def blink_button(self, button, times=3):
        """สร้างอนิเมชันกะพริบให้ปุ่ม"""
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
        """Set all button states with visual feedback"""
        current_select = self.select_button.cget("state")
        current_start = self.start_button.cget("state")
        current_stop = self.stop_button.cget("state")

        # ตั้งค่าสถานะปุ่ม
        self.select_button.config(state=select_state)
        self.start_button.config(state=start_state)
        self.stop_button.config(state=stop_state)

        # แสดงอนิเมชันสำหรับปุ่มที่เปิดใช้งาน
        if stop_state == "normal" and current_stop == "disabled":
            self.blink_button(self.stop_button, 3)

    def start_animation(self):
        """Start gauge line animation"""
        self.is_animating = True
        self.animation_thread = threading.Thread(
            target=self._animation_loop, daemon=True
        )
        self.animation_thread.start()

    def stop_animation(self):
        """Stop animation"""
        self.is_animating = False

    def _animation_loop(self):
        """Animation loop for the gauge indicator with smooth movement"""
        position = 0.5
        direction = 0.01

        # Animation variables for smooth movement
        amplitude = 0.45  # Max deviation from center
        period = 15.0  # Time for one complete cycle

        # Starting time
        start_time = time.time()

        while self.is_animating:
            # Only move line when not actually running
            if not hasattr(self.app, "running") or not self.app.running:
                # Use sine wave for smooth, natural-looking animation
                current_time = time.time() - start_time
                # Sinusoidal movement around center position
                position = 0.5 + amplitude * math.sin(
                    2 * math.pi * current_time / period
                )

                # Update position
                self.update_line_position(position)

                # Generate random bites/tugs for demo purposes
                if random.random() < 0.002:  # 0.2% chance per frame
                    # Simulate a fish bite with quick movement
                    self.simulate_bite()

            # Delay for smooth animation
            time.sleep(0.05)

    def simulate_bite(self):
        """Simulate a fish bite with quick movement"""
        # Starting position
        start_pos = 0.5
        # Target position (random within range)
        target_pos = random.uniform(0.1, 0.9)

        # ใช้ gauge widget สำหรับการจำลองการกระตุก
        self.gauge.simulate_bite(start_pos, 0.5, None)

    def show_tooltip(self, message, duration=2000):
        """Show temporary tooltip with pixelated style"""
        # Create tooltip window
        tooltip = tk.Toplevel(self.root)
        tooltip.overrideredirect(True)
        tooltip.attributes("-topmost", True)
        tooltip.configure(bg=self.bg_color)

        # Create pixel border with scanlines effect
        border = 2

        frame = tk.Frame(
            tooltip,
            bg=self.bg_color,
            highlightbackground=self.crt_color,
            highlightthickness=border,
            padx=10,
            pady=5,
        )
        frame.pack()

        # Create pixelated text with CRT glow effect
        shadow_label = tk.Label(
            frame,
            text=message,
            bg=self.bg_color,
            fg="#003300",  # Dark green shadow for CRT effect
            font=(UI_CONSTANTS["FONT_FAMILY"], 10, "bold"),
        )
        shadow_label.place(x=2, y=2)

        label = tk.Label(
            frame,
            text=message,
            bg=self.bg_color,
            fg=self.crt_color,
            font=(UI_CONSTANTS["FONT_FAMILY"], 10, "bold"),
        )
        label.pack()

        # Add scanlines effect
        canvas_width = label.winfo_reqwidth()
        canvas_height = label.winfo_reqheight()
        scanlines = tk.Canvas(
            frame,
            width=canvas_width,
            height=canvas_height,
            bg=self.bg_color,
            highlightthickness=0,
        )
        scanlines.pack(fill="both", expand=True)

        # Create semi-transparent scanlines
        for y in range(0, canvas_height, 2):
            scanlines.create_line(
                0, y, canvas_width, y, fill="#000000", stipple="gray25"
            )

        # Position tooltip
        tooltip.update_idletasks()
        width = tooltip.winfo_reqwidth()
        height = tooltip.winfo_reqheight()

        x = self.root.winfo_rootx() + (self.root.winfo_width() - width) // 2
        y = self.root.winfo_rooty() + 50

        tooltip.geometry(f"+{x}+{y}")

        # Add CRT turn-on effect
        tooltip.attributes("-alpha", 0.0)
        for i in range(10):
            if i == 5:
                # Flash brighter in the middle of the animation
                tooltip.configure(bg="#FFFFFF")
                frame.configure(bg="#FFFFFF")
            else:
                tooltip.configure(bg=self.bg_color)
                frame.configure(bg=self.bg_color)

            tooltip.attributes("-alpha", i / 10)
            tooltip.update()
            time.sleep(0.01)

        # Auto-destroy with CRT turn-off effect
        def fade_out():
            for i in range(10, -1, -1):
                tooltip.attributes("-alpha", i / 10)
                tooltip.update()
                time.sleep(0.01)
            tooltip.destroy()

        tooltip.after(duration, fade_out)
