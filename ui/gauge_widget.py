import tkinter as tk
import math
import random
import time


class PixelGauge:
    def __init__(self, parent, colors):
        """
        สร้างเกจแบบพิกเซลอาร์ตสำหรับการตกปลา

        Args:
            parent: Widget ที่จะเป็น parent ของ Canvas
            colors: Dictionary ที่เก็บค่าสีต่างๆ ที่ใช้ในเกจ
        """
        self.parent = parent
        self.colors = colors

        # ค่าสีที่ใช้ในเกจ
        self.success_color = colors.get("success", "#1de887")  # สีเขียว
        self.danger_color = colors.get("danger", "#c2002e")  # สีแดง
        self.warning_color = colors.get("warning", "#f9e04b")  # สีเหลือง
        self.bg_color = colors.get("bg", "#2e3440")  # สีพื้นหลัง
        self.accent_color = colors.get("accent", "#88c0d0")  # สีเน้น
        self.crt_color = colors.get("crt", "#eceff4")  # สีแสง CRT

        # สร้าง Canvas สำหรับเกจ
        self.canvas = tk.Canvas(
            parent, height=60, bg=self.bg_color, highlightthickness=0
        )
        self.canvas.pack(fill="x", pady=5)

        # ตัวแปรสำหรับเก็บรายการในเกจ
        self.gauge_line = None
        self.gauge_shadow = None
        self.gauge_arrow = None
        self.gauge_blinker = None
        self.gauge_indicators = []

        # ตัวแปรสำหรับการกะพริบ
        self.blink_state = False
        self.last_blink_time = time.time()

        # เรียกเมธอดสร้างเกจ
        self.create_pixel_gauge()

    def create_pixel_gauge(self):
        """สร้างเกจแบบพิกเซลที่มีรายละเอียดและแบ่งโซนอย่างชัดเจน"""
        # ตรวจสอบความกว้างของ canvas
        width = self.canvas.winfo_width()
        if width < 10:
            width = 380

        # ล้าง canvas
        self.canvas.delete("all")

        # สร้างกรอบเกจด้วยเส้นพิกเซล
        self.canvas.create_rectangle(
            0, 0, width, 60, outline=self.accent_color, width=1
        )

        # สร้างเส้นขอบด้านในแบบพิกเซล
        pixel_border_size = 2
        for i in range(0, width, pixel_border_size * 2):
            # เส้นขอบด้านบน
            self.canvas.create_rectangle(
                i,
                0,
                i + pixel_border_size,
                pixel_border_size,
                fill=self.crt_color,
                outline="",
            )
            # เส้นขอบด้านล่าง
            self.canvas.create_rectangle(
                i,
                60 - pixel_border_size,
                i + pixel_border_size,
                60,
                fill=self.crt_color,
                outline="",
            )

        for i in range(0, 60, pixel_border_size * 2):
            # เส้นขอบด้านซ้าย
            self.canvas.create_rectangle(
                0,
                i,
                pixel_border_size,
                i + pixel_border_size,
                fill=self.crt_color,
                outline="",
            )
            # เส้นขอบด้านขวา
            self.canvas.create_rectangle(
                width - pixel_border_size,
                i,
                width,
                i + pixel_border_size,
                fill=self.crt_color,
                outline="",
            )

        # พื้นที่ใช้งานจริงของเกจ (ภายในขอบ)
        gauge_padding = 4
        gauge_inner_width = width - (gauge_padding * 2)
        gauge_inner_height = 52

        # สร้างพื้นหลังพิกเซลด้วยลายตาราง
        cell_size = 4  # ขนาดพิกเซล
        rows = gauge_inner_height // cell_size
        cols = gauge_inner_width // cell_size

        # วาดพื้นหลังเป็นลายตาราง
        for row in range(rows):
            for col in range(cols):
                x1 = gauge_padding + (col * cell_size)
                y1 = gauge_padding + (row * cell_size)
                x2 = x1 + cell_size - 1  # -1 เพื่อสร้างเส้นตารางบาง
                y2 = y1 + cell_size - 1

                # ลายตารางสลับสี
                if (row + col) % 2 == 0:
                    color = self.bg_color
                else:
                    # สีที่เข้มกว่าเล็กน้อยเพื่อสร้างลายตาราง
                    r = max(0, int(int(self.bg_color[1:3], 16) * 0.8))
                    g = max(0, int(int(self.bg_color[3:5], 16) * 0.8))
                    b = max(0, int(int(self.bg_color[5:7], 16) * 0.8))
                    color = f"#{r:02x}{g:02x}{b:02x}"

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

        # กำหนดขนาดของแต่ละโซน
        red_zone_width = gauge_inner_width * 0.18
        buffer_width = gauge_inner_width * 0.07
        green_zone_width = gauge_inner_width - (2 * red_zone_width) - (2 * buffer_width)

        # สร้างพื้นหลังสีเข้มเพื่อให้โซนต่างๆ โดดเด่น
        self.canvas.create_rectangle(
            gauge_padding,
            gauge_padding,
            width - gauge_padding,
            gauge_padding + gauge_inner_height,
            fill="#1e2430",
            outline="",
        )

        # เพิ่มเส้นขีดบอกระยะเพื่อเพิ่มรายละเอียด
        tick_height = 2
        tick_spacing = gauge_inner_width / 20
        for i in range(21):  # 20 ช่วง = 21 เส้น
            x = gauge_padding + (i * tick_spacing)
            self.canvas.create_line(
                x,
                gauge_padding + gauge_inner_height - tick_height,
                x,
                gauge_padding + gauge_inner_height,
                fill="#717e96",
                width=1,
            )

        # สร้างไอคอน 8-bit สำหรับแสดงโซน
        self._draw_zone_icons(
            gauge_padding,
            gauge_inner_width,
            red_zone_width,
            buffer_width,
            green_zone_width,
            width,
        )

        # สร้างโซนสีต่างๆ ด้วยลายพิกเซล
        self._draw_colored_zones(
            gauge_padding,
            rows,
            cols,
            cell_size,
            red_zone_width,
            buffer_width,
            green_zone_width,
            width,
        )

        # สร้างเส้นแบ่งโซน
        self._draw_zone_dividers(
            gauge_padding, gauge_inner_height, red_zone_width, buffer_width, width
        )

        # สร้างเส้นกลาง
        self._draw_center_line(width, gauge_padding, gauge_inner_height)

        # เพิ่มป้ายกำกับโซน
        self._add_zone_labels(
            gauge_padding,
            gauge_inner_height,
            red_zone_width,
            buffer_width,
            green_zone_width,
            width,
        )

        # สร้างตัวชี้
        line_x = width / 2
        self._create_gauge_indicator(line_x, gauge_padding, gauge_inner_height)

        # เพิ่มเอฟเฟกต์เรืองแสงแบบ CRT
        self._add_glow_effect(line_x, gauge_padding + gauge_inner_height / 2)

    def _draw_zone_icons(
        self,
        gauge_padding,
        gauge_inner_width,
        red_zone_width,
        buffer_width,
        green_zone_width,
        width,
    ):
        """วาดไอคอนสำหรับแต่ละโซน"""
        # ไอคอนอันตราย (ซ้าย)
        danger_icon_left = ["  XX  ", " XXXX ", "XXXXXX", "XXXXXX", " XXXX ", "  XX  "]
        self._draw_pixel_icon(
            danger_icon_left,
            gauge_padding + red_zone_width / 2 - 12,
            gauge_padding + 5,
            self.danger_color,
        )

        # ไอคอนปลอดภัย (กลาง)
        safe_icon = ["      ", " XXXX ", "X    X", "X XX X", "X    X", " XXXX "]
        self._draw_pixel_icon(
            safe_icon,
            gauge_padding + red_zone_width + buffer_width + green_zone_width / 2 - 12,
            gauge_padding + 5,
            self.success_color,
        )

        # ไอคอนอันตราย (ขวา)
        danger_icon_right = ["  XX  ", " XXXX ", "XXXXXX", "XXXXXX", " XXXX ", "  XX  "]
        self._draw_pixel_icon(
            danger_icon_right,
            width - gauge_padding - red_zone_width / 2 - 12,
            gauge_padding + 5,
            self.danger_color,
        )

    def _draw_colored_zones(
        self,
        gauge_padding,
        rows,
        cols,
        cell_size,
        red_zone_width,
        buffer_width,
        green_zone_width,
        width,
    ):
        """วาดโซนสีต่างๆ ด้วยลายพิกเซล"""
        # โซนแดง (ซ้าย)
        for row in range(rows):
            for col in range(int(red_zone_width // cell_size)):
                x1 = gauge_padding + (col * cell_size)
                y1 = gauge_padding + (row * cell_size)
                x2 = x1 + cell_size - 1
                y2 = y1 + cell_size - 1

                # สร้างลายพิกเซลด้วยการสุ่มค่าความเข้มของสี
                intensity = 0.9 + (hash((row, col)) % 20) / 100
                r = min(255, int(int(self.danger_color[1:3], 16) * intensity))
                g = min(255, int(int(self.danger_color[3:5], 16) * intensity))
                b = min(255, int(int(self.danger_color[5:7], 16) * intensity))

                color = f"#{r:02x}{g:02x}{b:02x}"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

        # โซนบัฟเฟอร์ (ซ้าย)
        for row in range(rows):
            for col in range(int(buffer_width // cell_size)):
                x1 = gauge_padding + red_zone_width + (col * cell_size)
                y1 = gauge_padding + (row * cell_size)
                x2 = x1 + cell_size - 1
                y2 = y1 + cell_size - 1

                # ไล่ระดับสีจากแดงเป็นเขียว
                ratio = col / (buffer_width // cell_size)
                ratio_variant = ratio + (hash((row, col)) % 10) / 100 - 0.05
                ratio_variant = max(0, min(1, ratio_variant))

                r = int(
                    (1 - ratio_variant) * int(self.danger_color[1:3], 16)
                    + ratio_variant * int(self.success_color[1:3], 16)
                )
                g = int(
                    (1 - ratio_variant) * int(self.danger_color[3:5], 16)
                    + ratio_variant * int(self.success_color[3:5], 16)
                )
                b = int(
                    (1 - ratio_variant) * int(self.danger_color[5:7], 16)
                    + ratio_variant * int(self.success_color[5:7], 16)
                )

                color = f"#{r:02x}{g:02x}{b:02x}"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

        # โซนเขียว (กลาง)
        for row in range(rows):
            for col in range(int(green_zone_width // cell_size)):
                x1 = gauge_padding + red_zone_width + buffer_width + (col * cell_size)
                y1 = gauge_padding + (row * cell_size)
                x2 = x1 + cell_size - 1
                y2 = y1 + cell_size - 1

                # สร้างลายพิกเซลด้วยการสุ่มค่าความเข้มของสี
                intensity = 0.9 + (hash((row, col)) % 20) / 100
                r = min(255, int(int(self.success_color[1:3], 16) * intensity))
                g = min(255, int(int(self.success_color[3:5], 16) * intensity))
                b = min(255, int(int(self.success_color[5:7], 16) * intensity))

                color = f"#{r:02x}{g:02x}{b:02x}"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

        # โซนบัฟเฟอร์ (ขวา)
        for row in range(rows):
            for col in range(int(buffer_width // cell_size)):
                x1 = (
                    gauge_padding
                    + red_zone_width
                    + buffer_width
                    + green_zone_width
                    + (col * cell_size)
                )
                y1 = gauge_padding + (row * cell_size)
                x2 = x1 + cell_size - 1
                y2 = y1 + cell_size - 1

                # ไล่ระดับสีจากเขียวเป็นแดง
                ratio = col / (buffer_width // cell_size)
                ratio_variant = ratio + (hash((row, col)) % 10) / 100 - 0.05
                ratio_variant = max(0, min(1, ratio_variant))

                r = int(
                    (1 - ratio_variant) * int(self.success_color[1:3], 16)
                    + ratio_variant * int(self.danger_color[1:3], 16)
                )
                g = int(
                    (1 - ratio_variant) * int(self.success_color[3:5], 16)
                    + ratio_variant * int(self.danger_color[3:5], 16)
                )
                b = int(
                    (1 - ratio_variant) * int(self.success_color[5:7], 16)
                    + ratio_variant * int(self.danger_color[5:7], 16)
                )

                color = f"#{r:02x}{g:02x}{b:02x}"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

        # โซนแดง (ขวา)
        for row in range(rows):
            for col in range(int(red_zone_width // cell_size)):
                x1 = width - gauge_padding - red_zone_width + (col * cell_size)
                y1 = gauge_padding + (row * cell_size)
                x2 = x1 + cell_size - 1
                y2 = y1 + cell_size - 1

                # สร้างลายพิกเซลด้วยการสุ่มค่าความเข้มของสี
                intensity = 0.9 + (hash((row, col)) % 20) / 100
                r = min(255, int(int(self.danger_color[1:3], 16) * intensity))
                g = min(255, int(int(self.danger_color[3:5], 16) * intensity))
                b = min(255, int(int(self.danger_color[5:7], 16) * intensity))

                color = f"#{r:02x}{g:02x}{b:02x}"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

    def _draw_zone_dividers(
        self, gauge_padding, gauge_inner_height, red_zone_width, buffer_width, width
    ):
        """วาดเส้นแบ่งโซน"""
        zone_divider_width = 3
        for x in [
            gauge_padding + red_zone_width,
            gauge_padding + red_zone_width + buffer_width,
            width - gauge_padding - red_zone_width - buffer_width,
            width - gauge_padding - red_zone_width,
        ]:
            # สร้างเส้นแบ่งแบบพิกเซล
            for i in range(gauge_padding, gauge_padding + gauge_inner_height, 6):
                self.canvas.create_rectangle(
                    x - zone_divider_width // 2,
                    i,
                    x + zone_divider_width // 2,
                    i + 4,
                    fill=self.crt_color,
                    outline="",
                )

    def _draw_center_line(self, width, gauge_padding, gauge_inner_height):
        """วาดเส้นกลาง"""
        center_x = width / 2
        for i in range(gauge_padding, gauge_padding + gauge_inner_height, 6):
            self.canvas.create_rectangle(
                center_x - 1, i, center_x + 1, i + 3, fill=self.crt_color, outline=""
            )

    def _add_zone_labels(
        self,
        gauge_padding,
        gauge_inner_height,
        red_zone_width,
        buffer_width,
        green_zone_width,
        width,
    ):
        """เพิ่มป้ายกำกับโซน"""
        label_y = gauge_padding + gauge_inner_height + 3

        # ซ้าย (อันตราย)
        self.canvas.create_text(
            gauge_padding + red_zone_width / 2,
            label_y,
            text="DANGER",
            fill=self.danger_color,
            font=("Courier", 7, "bold"),
        )

        # ซ้าย (ระวัง)
        self.canvas.create_text(
            gauge_padding + red_zone_width + buffer_width / 2,
            label_y,
            text="CAUTION",
            fill=self.warning_color,
            font=("Courier", 7, "bold"),
        )

        # กลาง (ปลอดภัย)
        self.canvas.create_text(
            gauge_padding + red_zone_width + buffer_width + green_zone_width / 2,
            label_y,
            text="SAFE ZONE",
            fill=self.success_color,
            font=("Courier", 7, "bold"),
        )

        # ขวา (ระวัง)
        self.canvas.create_text(
            width - gauge_padding - red_zone_width - buffer_width / 2,
            label_y,
            text="CAUTION",
            fill=self.warning_color,
            font=("Courier", 7, "bold"),
        )

        # ขวา (อันตราย)
        self.canvas.create_text(
            width - gauge_padding - red_zone_width / 2,
            label_y,
            text="DANGER",
            fill=self.danger_color,
            font=("Courier", 7, "bold"),
        )

    def _create_gauge_indicator(self, line_x, gauge_padding, gauge_inner_height):
        """สร้างตัวชี้ตำแหน่ง"""
        # สร้างเงาตัวชี้
        self.gauge_shadow = self.canvas.create_rectangle(
            line_x - 3,
            gauge_padding,
            line_x + 3,
            gauge_padding + gauge_inner_height,
            fill="#000000",
            outline="",
            stipple="gray25",
        )

        # สร้างเส้นตัวชี้หลัก
        self.gauge_line = self.canvas.create_line(
            line_x,
            gauge_padding,
            line_x,
            gauge_padding + gauge_inner_height,
            fill=self.crt_color,
            width=3,
        )

        # สร้างหัวลูกศรด้านบน
        arrow_size = 8
        self.gauge_arrow = self.canvas.create_polygon(
            line_x - arrow_size,
            gauge_padding,
            line_x + arrow_size,
            gauge_padding,
            line_x,
            gauge_padding + arrow_size + 2,
            fill=self.crt_color,
            outline="",
        )

        # สร้างไฟกะพริบด้านล่าง
        self.gauge_blinker = self.canvas.create_oval(
            line_x - 4,
            gauge_padding + gauge_inner_height - 8,
            line_x + 4,
            gauge_padding + gauge_inner_height,
            fill=self.accent_color,
            outline=self.crt_color,
            width=1,
        )

    def _add_glow_effect(self, x, y, radius=10):
        """เพิ่มเอฟเฟกต์เรืองแสงแบบ CRT"""
        for r in range(radius, 0, -1):
            opacity = (radius - r) / radius  # ยิ่งห่างยิ่งโปร่งใส
            stipple = "gray25" if r > radius / 2 else "gray50"
            self.canvas.create_oval(
                x - r,
                y - r,
                x + r,
                y + r,
                outline=self.crt_color,
                width=1,
                stipple=stipple,
            )

    def _draw_pixel_icon(self, icon_data, x, y, color):
        """วาดไอคอนแบบพิกเซล"""
        pixel_size = 4
        for row, line in enumerate(icon_data):
            for col, pixel in enumerate(line):
                if pixel == "X":
                    self.canvas.create_rectangle(
                        x + col * pixel_size,
                        y + row * pixel_size,
                        x + (col + 1) * pixel_size - 1,
                        y + (row + 1) * pixel_size - 1,
                        fill=color,
                        outline="",
                    )

    def update_position(self, relative_pos):
        """อัปเดตตำแหน่งของตัวชี้ในเกจ

        Args:
            relative_pos: ตำแหน่งสัมพัทธ์ (0.0 - 1.0)

        Returns:
            tuple: (zone_type, position_text)
                zone_type: "danger", "warning", "safe"
                position_text: "LEFT", "RIGHT", "LEFT-MID", "RIGHT-MID", "CENTER"
        """
        width = self.canvas.winfo_width()
        if width < 10:
            width = 380

        gauge_padding = 4
        gauge_inner_height = 52

        line_x = width * relative_pos

        # อัปเดตเส้นตัวชี้
        self.canvas.coords(
            self.gauge_line,
            line_x,
            gauge_padding,
            line_x,
            gauge_padding + gauge_inner_height,
        )

        # อัปเดตเงา
        self.canvas.coords(
            self.gauge_shadow,
            line_x - 3,
            gauge_padding,
            line_x + 3,
            gauge_padding + gauge_inner_height,
        )

        # อัปเดตหัวลูกศร
        arrow_size = 8
        self.canvas.coords(
            self.gauge_arrow,
            line_x - arrow_size,
            gauge_padding,
            line_x + arrow_size,
            gauge_padding,
            line_x,
            gauge_padding + arrow_size + 2,
        )

        # อัปเดตไฟกะพริบ
        self.canvas.coords(
            self.gauge_blinker,
            line_x - 4,
            gauge_padding + gauge_inner_height - 8,
            line_x + 4,
            gauge_padding + gauge_inner_height,
        )

        # กำหนดสีตามโซน
        if relative_pos < 0.25:
            blinker_color = self.danger_color
            zone_type = "danger"
            position_text = "LEFT"
        elif relative_pos > 0.75:
            blinker_color = self.danger_color
            zone_type = "danger"
            position_text = "RIGHT"
        elif 0.25 <= relative_pos < 0.35:
            blinker_color = self.warning_color
            zone_type = "warning"
            position_text = "LEFT-MID"
        elif 0.65 < relative_pos <= 0.75:
            blinker_color = self.warning_color
            zone_type = "warning"
            position_text = "RIGHT-MID"
        else:
            blinker_color = self.crt_color
            zone_type = "safe"
            position_text = "CENTER"

        # อัปเดตสีไฟกะพริบ
        self.canvas.itemconfig(self.gauge_blinker, fill=blinker_color)

        # เอฟเฟกต์กะพริบเมื่ออยู่ในโซนอันตราย
        current_time = time.time()
        if (
            relative_pos < 0.25 or relative_pos > 0.75
        ) and current_time - self.last_blink_time > 0.25:
            self.blink_state = not self.blink_state
            self.last_blink_time = current_time

            if self.blink_state:
                self.canvas.itemconfig(self.gauge_blinker, fill=blinker_color)
            else:
                self.canvas.itemconfig(self.gauge_blinker, fill="#000000")

        return zone_type, position_text

    def simulate_bite(self, start_pos=0.5, duration=0.5, callback=None):
        """จำลองการกระตุกของปลา

        Args:
            start_pos: ตำแหน่งเริ่มต้น (ค่าเริ่มต้น: 0.5)
            duration: ระยะเวลาของการกระตุก (วินาที)
            callback: ฟังก์ชันที่จะเรียกเมื่อสิ้นสุดการกระตุก
        """
        # กำหนดช่วงเวลา
        fps = 30
        steps = int(duration * fps)
        step_time = int(1000 / fps)  # มิลลิวินาที

        # กำหนดตำแหน่งเป้าหมาย
        target_pos = random.uniform(0.1, 0.9)

        # อนิเมชันการกระตุก
        def animate_bite(step=0):
            if step >= steps:
                if callback:
                    callback()
                return

            # คำนวณตำแหน่งปัจจุบัน
            progress = step / steps
            easing = 1 - math.pow(1 - progress, 3)  # Ease out cubic
            current_pos = start_pos + (target_pos - start_pos) * easing

            # อัปเดตตำแหน่ง
            self.update_position(current_pos)

            # ทำซ้ำตามจำนวนเฟรม
            self.canvas.after(step_time, lambda: animate_bite(step + 1))

        # เริ่มอนิเมชัน
        animate_bite()

    def set_gauge_color(
        self,
        success_color=None,
        danger_color=None,
        warning_color=None,
        accent_color=None,
        crt_color=None,
    ):
        """เปลี่ยนสีของเกจ

        Args:
            success_color: สีโซนปลอดภัย
            danger_color: สีโซนอันตราย
            warning_color: สีโซนเตือน
            accent_color: สีเน้น
            crt_color: สีแสง CRT
        """
        # อัปเดตค่าสี
        if success_color:
            self.success_color = success_color
        if danger_color:
            self.danger_color = danger_color
        if warning_color:
            self.warning_color = warning_color
        if accent_color:
            self.accent_color = accent_color
        if crt_color:
            self.crt_color = crt_color

        # สร้างเกจใหม่
        self.create_pixel_gauge()

    def reset(self, start_position=0.5):
        """รีเซ็ตเกจไปที่ตำแหน่งเริ่มต้น

        Args:
            start_position: ตำแหน่งเริ่มต้น (ค่าเริ่มต้น: 0.5)
        """
        # สร้างเกจใหม่
        self.create_pixel_gauge()

        # อัปเดตตำแหน่ง
        self.update_position(start_position)
