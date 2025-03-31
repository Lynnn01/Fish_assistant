import tkinter as tk
from tkinter import ttk
import time
import threading


class PixelatedUI:
    def __init__(self, root, app):
        self.root = root
        self.app = app

        # Pixel art color palette
        self.primary_color = "#5e81ac"  # Deep blue
        self.secondary_color = "#d08770"  # Salmon
        self.success_color = "#a3be8c"  # Moss green
        self.danger_color = "#bf616a"  # Rusty red
        self.warning_color = "#ebcb8b"  # Mustard yellow
        self.bg_color = "#2e3440"  # Dark background
        self.text_color = "#eceff4"  # Light text
        self.panel_bg = "#3b4252"  # Slightly lighter panel background
        self.accent_color = "#88c0d0"  # Accent blue

        # Animation
        self.is_animating = False
        self.animation_thread = None

        # Configure the root window for pixel art style
        self.root.configure(bg=self.bg_color)
        self.root.option_add("*Font", "Courier 10")  # Pixel-like font

        # Create UI components
        self.create_ui()

        # Start animation
        self.start_animation()

    def create_ui(self):
        """Create pixel art styled UI"""
        # Configure style for widgets
        style = ttk.Style()
        style.theme_use("default")

        # Configure button styles with pixel-like appearance
        style.configure(
            "Pixel.TButton",
            font=("Courier", 10, "bold"),
            background=self.primary_color,
            foreground=self.text_color,
            borderwidth=2,
            relief="raised",
        )

        style.configure(
            "PixelSuccess.TButton",
            font=("Courier", 10, "bold"),
            background=self.success_color,
            foreground=self.text_color,
            borderwidth=2,
            relief="raised",
        )

        style.configure(
            "PixelDanger.TButton",
            font=("Courier", 10, "bold"),
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
            font=("Courier", 10),
        )
        style.configure(
            "PixelTitle.TLabel",
            background=self.bg_color,
            foreground=self.accent_color,
            font=("Courier", 12, "bold"),
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
            font=("Courier", 10, "bold"),
        )

        # Main frame
        main_frame = ttk.Frame(self.root, style="Pixel.TFrame", padding=15)
        main_frame.pack(fill="both", expand=True)

        # Header section with pixelated title
        header_frame = ttk.Frame(main_frame, style="PixelPanel.TFrame")
        header_frame.pack(fill="x", pady=(0, 15), ipady=5)

        title_label = tk.Label(
            header_frame,
            text="╔══════════════════════╗\n║  FISHING ASSISTANT BOT  ║\n╚══════════════════════╝",
            font=("Courier", 14, "bold"),
            fg=self.accent_color,
            bg=self.panel_bg,
            justify="center",
        )
        title_label.pack(pady=10)

        # Instruction text
        tip_frame = ttk.Frame(main_frame, style="Pixel.TFrame")
        tip_frame.pack(fill="x", pady=5)

        tip_text = ttk.Label(
            tip_frame,
            text="▶ SELECT REGION WITH GAUGE AND PRESS START ◀",
            style="PixelTitle.TLabel",
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

        # Gauge visualization
        gauge_frame = ttk.LabelFrame(
            main_frame, text="GAUGE", style="Pixel.TLabelframe", padding=10
        )
        gauge_frame.pack(fill="x", pady=10)

        self.gauge_canvas = tk.Canvas(
            gauge_frame, height=50, bg=self.bg_color, highlightthickness=0
        )
        self.gauge_canvas.pack(fill="x", pady=5)

        # Create pixelated gauge
        self.create_pixel_gauge()

        # Indicator data
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
            footer_frame,
            text="╔═════════════════════════════╗\n║  PRESS 'F10' TO STOP ANYTIME  ║\n╚═════════════════════════════╝",
            foreground=self.danger_color,
            background=self.bg_color,
            font=("Courier", 10, "bold"),
        )
        hotkey_label.pack(pady=5)

        # Version
        version_label = ttk.Label(footer_frame, text="v1.0", style="Pixel.TLabel")
        version_label.pack(side="right", padx=5)

    def create_pixel_gauge(self):
        """Create a pixelated gauge"""
        # Get canvas width
        width = self.gauge_canvas.winfo_width()
        if width < 10:
            width = 380

        # Clear canvas
        self.gauge_canvas.delete("all")

        # Create pixelated background with grid pattern
        cell_size = 5  # Pixel size
        rows = 10
        cols = width // cell_size

        # Draw background grid
        for row in range(rows):
            for col in range(cols):
                x1 = col * cell_size
                y1 = row * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size

                # Alternate pattern for grid effect
                if (row + col) % 2 == 0:
                    color = self.panel_bg
                else:
                    color = self.bg_color

                self.gauge_canvas.create_rectangle(
                    x1, y1, x2, y2, fill=color, outline=""
                )

        # Calculate zone sizes
        red_zone_width = width * 0.2
        buffer_width = width * 0.05
        green_zone_width = width - (2 * red_zone_width) - (2 * buffer_width)

        # Create red zone (left)
        for row in range(rows):
            for col in range(int(red_zone_width // cell_size)):
                x1 = col * cell_size
                y1 = row * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                self.gauge_canvas.create_rectangle(
                    x1, y1, x2, y2, fill=self.danger_color, outline=""
                )

        # Create buffer zone (left)
        for row in range(rows):
            for col in range(int(buffer_width // cell_size)):
                x1 = red_zone_width + col * cell_size
                y1 = row * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size

                # Transition from red to green
                ratio = col / (buffer_width // cell_size)
                r = int(
                    (1 - ratio) * int(self.danger_color[1:3], 16)
                    + ratio * int(self.success_color[1:3], 16)
                )
                g = int(
                    (1 - ratio) * int(self.danger_color[3:5], 16)
                    + ratio * int(self.success_color[3:5], 16)
                )
                b = int(
                    (1 - ratio) * int(self.danger_color[5:7], 16)
                    + ratio * int(self.success_color[5:7], 16)
                )

                color = f"#{r:02x}{g:02x}{b:02x}"
                self.gauge_canvas.create_rectangle(
                    x1, y1, x2, y2, fill=color, outline=""
                )

        # Create green zone (center)
        for row in range(rows):
            for col in range(int(green_zone_width // cell_size)):
                x1 = (red_zone_width + buffer_width) + col * cell_size
                y1 = row * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                self.gauge_canvas.create_rectangle(
                    x1, y1, x2, y2, fill=self.success_color, outline=""
                )

        # Create buffer zone (right)
        for row in range(rows):
            for col in range(int(buffer_width // cell_size)):
                x1 = (
                    red_zone_width + buffer_width + green_zone_width
                ) + col * cell_size
                y1 = row * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size

                # Transition from green to red
                ratio = col / (buffer_width // cell_size)
                r = int(
                    (1 - ratio) * int(self.success_color[1:3], 16)
                    + ratio * int(self.danger_color[1:3], 16)
                )
                g = int(
                    (1 - ratio) * int(self.success_color[3:5], 16)
                    + ratio * int(self.danger_color[3:5], 16)
                )
                b = int(
                    (1 - ratio) * int(self.success_color[5:7], 16)
                    + ratio * int(self.danger_color[5:7], 16)
                )

                color = f"#{r:02x}{g:02x}{b:02x}"
                self.gauge_canvas.create_rectangle(
                    x1, y1, x2, y2, fill=color, outline=""
                )

        # Create red zone (right)
        for row in range(rows):
            for col in range(int(red_zone_width // cell_size)):
                x1 = (width - red_zone_width) + col * cell_size
                y1 = row * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                self.gauge_canvas.create_rectangle(
                    x1, y1, x2, y2, fill=self.danger_color, outline=""
                )

        # Create zone dividers with pixelated look
        for x in [
            red_zone_width,
            red_zone_width + buffer_width,
            width - red_zone_width - buffer_width,
            width - red_zone_width,
        ]:
            for i in range(0, 50, 6):  # Dotted line effect
                self.gauge_canvas.create_rectangle(
                    x - 1, i, x + 1, i + 3, fill=self.text_color, outline=""
                )

        # Create center line
        for i in range(0, 50, 6):
            self.gauge_canvas.create_rectangle(
                width / 2 - 1, i, width / 2 + 1, i + 3, fill=self.text_color, outline=""
            )

        # Create indicator line
        line_x = width / 2
        self.gauge_line = self.gauge_canvas.create_line(
            line_x, 0, line_x, 50, fill=self.accent_color, width=2
        )

        # Create pixel-style indicator cap
        self.gauge_indicators = []
        for i in range(5):
            y = i * 3
            ind = self.gauge_canvas.create_rectangle(
                line_x - 3, y, line_x + 3, y + 2, fill=self.accent_color, outline=""
            )
            self.gauge_indicators.append(ind)

    def create_pixel_progress_bar(self):
        """Create a pixelated progress bar"""
        width = self.progress_canvas.winfo_width()
        if width < 10:
            width = 380

        # Clear existing blocks
        for block in self.progress_blocks:
            self.progress_canvas.delete(block)
        self.progress_blocks = []

        # Create new blocks
        block_width = 10
        num_blocks = width // block_width
        spacing = 2

        for i in range(num_blocks):
            x1 = i * block_width + spacing
            y1 = 2
            x2 = (i + 1) * block_width - spacing
            y2 = 13

            block = self.progress_canvas.create_rectangle(
                x1, y1, x2, y2, fill=self.bg_color, outline=self.panel_bg
            )
            self.progress_blocks.append(block)

    def update_progress_bar(self, value):
        """Update the pixelated progress bar"""
        if not self.progress_blocks:
            return

        num_blocks = len(self.progress_blocks)
        active_blocks = int((value / 100) * num_blocks)

        for i, block in enumerate(self.progress_blocks):
            if i < active_blocks:
                if value < 30:
                    color = self.danger_color
                elif value < 70:
                    color = self.warning_color
                else:
                    color = self.success_color
            else:
                color = self.bg_color

            self.progress_canvas.itemconfig(block, fill=color)

    def update_line_position(self, relative_pos):
        """Update the position of the indicator line in the gauge"""
        width = self.gauge_canvas.winfo_width()
        if width < 10:
            width = 380

        line_x = width * relative_pos
        self.gauge_canvas.coords(self.gauge_line, line_x, 0, line_x, 50)

        # Update indicator blocks
        for ind in self.gauge_indicators:
            coords = self.gauge_canvas.coords(ind)
            self.gauge_canvas.coords(ind, line_x - 3, coords[1], line_x + 3, coords[3])

        # Update position info
        if relative_pos < 0.25:
            self.position_value.config(text="LEFT")
            self.zone_value.config(text="WARNING", foreground=self.warning_color)
        elif relative_pos > 0.75:
            self.position_value.config(text="RIGHT")
            self.zone_value.config(text="DANGER", foreground=self.danger_color)
        else:
            self.position_value.config(text="CENTER")
            self.zone_value.config(text="SAFE", foreground=self.success_color)

    def update_status(self, text, status_type="normal"):
        """Update status message"""
        self.status_label.config(text=text.upper())

        if status_type == "success":
            self.status_label.config(foreground=self.success_color)
            self.update_progress_bar(100)
        elif status_type == "danger":
            self.status_label.config(foreground=self.danger_color)
            self.update_progress_bar(0)
        elif status_type == "warning":
            self.status_label.config(foreground=self.warning_color)
            # Simulate indeterminate progress
            self.start_progress_animation()
        else:
            self.status_label.config(foreground=self.text_color)
            self.update_progress_bar(50)

    def start_progress_animation(self):
        """Start progress bar animation"""
        # Implementation would animate through progress blocks
        # For simplicity, we'll just update to 50%
        self.update_progress_bar(50)

    def update_region_info(self, region):
        """Update selected region information"""
        if region:
            x1, y1, x2, y2 = region
            size = f"{x2-x1}x{y2-y1}"
            self.region_label.config(text=f"({x1},{y1})-({x2},{y2}) [{size}]")
            self.show_tooltip(f"REGION: {size}")

    def set_start_button_state(self, state):
        """Set start button state"""
        self.start_button.config(state=state)

    def set_button_states(self, select_state, start_state, stop_state):
        """Set all button states"""
        self.select_button.config(state=select_state)
        self.start_button.config(state=start_state)
        self.stop_button.config(state=stop_state)

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
        """Animation loop for the gauge indicator"""
        position = 0.5
        direction = 0.01

        while self.is_animating:
            # Only move line when not actually running
            if not hasattr(self.app, "running") or not self.app.running:
                # Change direction at edges
                if position >= 0.95:
                    direction = -0.01
                elif position <= 0.05:
                    direction = 0.01

                # Update position
                position += direction
                self.update_line_position(position)

            # Delay
            time.sleep(0.05)

    def show_tooltip(self, message, duration=2000):
        """Show temporary tooltip"""
        # Create tooltip window
        tooltip = tk.Toplevel(self.root)
        tooltip.overrideredirect(True)
        tooltip.attributes("-topmost", True)
        tooltip.configure(bg=self.bg_color)

        # Create frame with pixel border
        frame = tk.Frame(
            tooltip,
            bg=self.bg_color,
            highlightbackground=self.accent_color,
            highlightthickness=2,
            padx=10,
            pady=5,
        )
        frame.pack()

        # Create pixelated style message
        label = tk.Label(
            frame,
            text=message,
            bg=self.bg_color,
            fg=self.accent_color,
            font=("Courier", 10, "bold"),
        )
        label.pack()

        # Position
        tooltip.update_idletasks()
        width = tooltip.winfo_reqwidth()
        height = tooltip.winfo_reqheight()

        x = self.root.winfo_rootx() + (self.root.winfo_width() - width) // 2
        y = self.root.winfo_rooty() + 50

        tooltip.geometry(f"+{x}+{y}")

        # Auto-destroy
        tooltip.after(duration, tooltip.destroy)
