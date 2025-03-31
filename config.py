class BotConfig:
    """คลาสสำหรับเก็บการตั้งค่าของบอท"""

    def __init__(self):
        # การตั้งค่าการตรวจจับ
        self.red_zone_threshold = 0.2  # ระยะห่างจากขอบที่ถือว่าเป็นโซนแดง (0.0-1.0)
        self.buffer_zone_size = 0.15  # โซนกันชนก่อนถึงโซนแดง (0.0-1.0)
        self.line_threshold = 200  # ความสว่างขั้นต่ำสำหรับเส้นขาว (0-255)
        self.color_threshold = 30  # ความแตกต่างของสีขั้นต่ำ

        # การตั้งค่าการคลิก
        self.action_cooldown = 0.1  # ระยะเวลาระหว่างการคลิกแต่ละครั้ง (วินาที)

        # การตั้งค่าการจัดการเมื่อเกจหายไป
        self.first_click_delay = 1.0  # ระยะเวลารอก่อนคลิกครั้งแรกหลังเกจหาย (วินาที)
        self.periodic_click_interval = 4.0  # ระยะเวลาระหว่างการคลิกเมื่อเกจหายไป (วินาที)

        # การตั้งค่า UI
        self.ui_colors = {
            "primary": "#3498db",  # สีน้ำเงิน
            "success": "#2ecc71",  # สีเขียว
            "danger": "#e74c3c",  # สีแดง
            "warning": "#f39c12",  # สีส้ม
            "background": "#f5f5f5",  # สีพื้นหลัง
        }

    def load_from_file(self, filename):
        """โหลดการตั้งค่าจากไฟล์"""
        try:
            import json

            with open(filename, "r") as file:
                config_data = json.load(file)

            # อัปเดตการตั้งค่าจากไฟล์
            for key, value in config_data.items():
                if hasattr(self, key):
                    setattr(self, key, value)

            return True
        except Exception as e:
            print(f"Error loading config: {e}")
            return False

    def save_to_file(self, filename):
        """บันทึกการตั้งค่าลงไฟล์"""
        try:
            import json

            # สร้าง dictionary จากคุณสมบัติของคลาส
            config_data = {
                "red_zone_threshold": self.red_zone_threshold,
                "buffer_zone_size": self.buffer_zone_size,
                "line_threshold": self.line_threshold,
                "color_threshold": self.color_threshold,
                "action_cooldown": self.action_cooldown,
                "first_click_delay": self.first_click_delay,
                "periodic_click_interval": self.periodic_click_interval,
                "ui_colors": self.ui_colors,
            }

            with open(filename, "w") as file:
                json.dump(config_data, file, indent=4)

            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
