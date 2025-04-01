import tkinter as tk
import time
import math


class PixelProgressBar:
    """Progress bar แบบพิกเซลอาร์ต"""

    def __init__(self, parent, colors, height=15):
        """
        สร้าง progress bar แบบพิกเซลอาร์ต

        Args:
            parent: Widget ที่จะเป็น parent
            colors: Dictionary ที่เก็บค่าสีต่างๆ
            height: ความสูงของ progress bar
        """
        self.parent = parent
        self.colors = colors

        # ดึงค่าสีจาก dictionary
        self.bg_color = colors.get("bg", "#2e3440")
        self.text_color = colors.get("text", "#eceff4")
        self.panel_bg = colors.get("panel_bg", "#3b4252")
        self.success_color = colors.get("success", "#a3be8c")
        self.danger_color = colors.get("danger", "#bf616a")
        self.warning_color = colors.get("warning", "#ebcb8b")

        # สร้าง Canvas
        self.canvas = tk.Canvas(
            parent, height=height, bg=self.bg_color, highlightthickness=0
        )
        self.canvas.pack(fill="x")

        # ตัวแปรของ progress bar
        self.blocks = []
        self.animation_active = False
        self.counter = 0

        # สร้าง progress bar
        self.create_progress_bar()

    def create_progress_bar(self):
        """สร้าง progress bar แบบพิกเซล"""
        width = self.canvas.winfo_width()
        if width < 10:
            width = 380

        # ล้างบล็อกเดิม
        for block in self.blocks:
            self.canvas.delete(block)
        self.blocks = []

        # สร้างกรอบ
        self.canvas.create_rectangle(
            0, 0, width, self.canvas.winfo_height(), outline=self.text_color, width=1
        )

        # กำหนดค่าต่างๆ ของบล็อก
        block_width = 10
        num_blocks = width // block_width - 1
        padding = 2

        # กำหนดจำนวนแถวของบล็อก
        rows = 3
        block_height = (self.canvas.winfo_height() - 2 * padding) / rows

        # สร้างบล็อก
        for i in range(num_blocks):
            for r in range(rows):
                x1 = i * block_width + padding
                y1 = padding + r * block_height
                x2 = (i + 1) * block_width - padding
                y2 = padding + (r + 1) * block_height - 1

                # สร้างบล็อกแบบพิกเซล
                block = self.canvas.create_rectangle(
                    x1, y1, x2, y2, fill=self.bg_color, outline=self.panel_bg, width=1
                )
                self.blocks.append(block)

    def update(self, value):
        """อัปเดตค่า progress

        Args:
            value: ค่า progress (0-100)
        """
        if not self.blocks:
            return

        num_blocks = len(self.blocks)
        active_blocks = int((value / 100) * num_blocks)

        # กำหนดสีตามค่า
        if value < 30:
            color = self.danger_color
        elif value < 70:
            color = self.warning_color
        else:
            color = self.text_color

        # อัปเดตสีของบล็อก
        for i, block in enumerate(self.blocks):
            if i < active_blocks:
                # เพิ่มเอฟเฟกต์แบบพิกเซลด้วยการสุ่มค่าความเข้มของสี
                intensity = 0.8 + (hash((i, int(time.time() * 5) % 10)) % 30) / 100

                # แปลงสีเป็นค่า RGB
                if len(color) == 7:  # สีในรูปแบบ #RRGGBB
                    r = int(color[1:3], 16)
                    g = int(color[3:5], 16)
                    b = int(color[5:7], 16)
                else:
                    # ใช้สีเดิมหากรูปแบบไม่ถูกต้อง
                    self.canvas.itemconfig(block, fill=color)
                    continue

                # ปรับความเข้มของสี
                r = min(255, int(r * intensity))
                g = min(255, int(g * intensity))
                b = min(255, int(b * intensity))

                # สร้างสีใหม่
                block_color = f"#{r:02x}{g:02x}{b:02x}"

                # ตรวจสอบความถูกต้องของสี
                if len(block_color) != 7:
                    block_color = color

                self.canvas.itemconfig(block, fill=block_color)
            else:
                self.canvas.itemconfig(block, fill=self.bg_color)

    def start_animation(self):
        """เริ่มการแสดงผลแบบเคลื่อนไหว (indeterminate)"""
        self.counter = 0
        if not self.animation_active:
            self.animation_active = True
            self._animate()

    def _animate(self):
        """แสดงผลการเคลื่อนไหวแบบต่อเนื่อง"""
        if not self.animation_active:
            return

        # รูปแบบการเคลื่อนไหวแบบเลื่อนไปมา
        self.counter = (self.counter + 5) % 100
        self.update(self.counter)

        # ทำซ้ำ
        self.canvas.after(100, self._animate)

    def stop_animation(self):
        """หยุดการแสดงผลแบบเคลื่อนไหว"""
        self.animation_active = False
        self.update(0)

    def pulse(self, value=100, duration=1000):
        """แสดงผลแบบกระพริบครั้งเดียว

        Args:
            value: ค่าสูงสุดที่จะแสดง (0-100)
            duration: ระยะเวลา (มิลลิวินาที)
        """
        # แสดงผลทันที
        self.update(value)

        # กำหนดให้กลับมาที่ 0 หลังจาก duration
        self.canvas.after(duration, lambda: self.update(0))
