import tkinter as tk
import time


class PixelTooltip:
    """Tooltip แบบพิกเซลอาร์ตพร้อมเอฟเฟกต์ CRT"""

    def __init__(self, root, message, colors, font_family="Courier", duration=2000):
        """
        สร้าง tooltip แบบพิกเซลอาร์ต

        Args:
            root: หน้าต่างหลัก
            message: ข้อความที่จะแสดง
            colors: Dictionary ที่เก็บค่าสีต่างๆ
            font_family: ฟอนต์ที่ใช้
            duration: ระยะเวลาที่แสดง (มิลลิวินาที)
        """
        self.root = root
        self.message = message
        self.duration = duration

        # ดึงค่าสีจาก dictionary
        self.bg_color = colors.get("bg", "#2e3440")
        self.text_color = colors.get("text", "#eceff4")

        # สร้าง tooltip
        self.tooltip = None
        self.frame = None
        self.shadow_label = None
        self.label = None
        self.scanlines = None

        # แสดง tooltip
        self.show()

    def show(self):
        """แสดง tooltip"""
        # สร้างหน้าต่าง tooltip
        self.tooltip = tk.Toplevel(self.root)
        self.tooltip.overrideredirect(True)
        self.tooltip.attributes("-topmost", True)
        self.tooltip.configure(bg=self.bg_color)

        # สร้างกรอบพร้อมขอบแบบพิกเซล
        border = 2
        self.frame = tk.Frame(
            self.tooltip,
            bg=self.bg_color,
            highlightbackground=self.text_color,
            highlightthickness=border,
            padx=10,
            pady=5,
        )
        self.frame.pack()

        # สร้างเงาของข้อความเพื่อเอฟเฟกต์ CRT
        self.shadow_label = tk.Label(
            self.frame,
            text=self.message,
            bg=self.bg_color,
            fg="#003300",  # สีเงา
            font=("Courier", 10, "bold"),
        )
        self.shadow_label.place(x=2, y=2)

        # สร้างข้อความหลัก
        self.label = tk.Label(
            self.frame,
            text=self.message,
            bg=self.bg_color,
            fg=self.text_color,
            font=("Courier", 10, "bold"),
        )
        self.label.pack()

        # สร้าง scanlines เพื่อเอฟเฟกต์ CRT
        canvas_width = self.label.winfo_reqwidth()
        canvas_height = self.label.winfo_reqheight()
        self.scanlines = tk.Canvas(
            self.frame,
            width=canvas_width,
            height=canvas_height,
            bg=self.bg_color,
            highlightthickness=0,
        )
        self.scanlines.pack(fill="both", expand=True)

        # สร้าง scanlines แบบโปร่งใส
        for y in range(0, canvas_height, 2):
            self.scanlines.create_line(
                0, y, canvas_width, y, fill="#000000", stipple="gray25"
            )

        # จัดตำแหน่ง tooltip
        self.tooltip.update_idletasks()
        width = self.tooltip.winfo_reqwidth()
        height = self.tooltip.winfo_reqheight()

        x = self.root.winfo_rootx() + (self.root.winfo_width() - width) // 2
        y = self.root.winfo_rooty() + 50

        self.tooltip.geometry(f"+{x}+{y}")

        # เอฟเฟกต์การแสดงผลแบบ CRT
        self._fade_in()

        # ตั้งเวลาปิด tooltip
        self.tooltip.after(self.duration, self._fade_out)

    def _fade_in(self):
        """เอฟเฟกต์เปิดหน้าจอ CRT"""
        self.tooltip.attributes("-alpha", 0.0)
        for i in range(10):
            if i == 5:
                # เอฟเฟกต์แฟลชสีขาวช่วงกลาง
                self.tooltip.configure(bg="#FFFFFF")
                self.frame.configure(bg="#FFFFFF")
            else:
                self.tooltip.configure(bg=self.bg_color)
                self.frame.configure(bg=self.bg_color)

            self.tooltip.attributes("-alpha", i / 10)
            self.tooltip.update()
            time.sleep(0.01)

    def _fade_out(self):
        """เอฟเฟกต์ปิดหน้าจอ CRT"""
        for i in range(10, -1, -1):
            self.tooltip.attributes("-alpha", i / 10)
            self.tooltip.update()
            time.sleep(0.01)
        self.tooltip.destroy()
