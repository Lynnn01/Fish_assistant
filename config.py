import json


class BotConfig:
    """คลาสสำหรับเก็บและจัดการการตั้งค่าของบอท"""

    def __init__(self, config_file=None):
        # การตั้งค่าการตรวจจับ
        self.red_zone_threshold = 0.2
        self.buffer_zone_size = 0.13
        self.line_threshold = 200
        self.color_threshold = 30

        # การตั้งค่าการคลิก
        self.action_cooldown = 0.1

        # การตั้งค่าการจัดการเมื่อเกจหายไป
        self.first_click_delay = 1.0
        self.periodic_click_interval = 4.0

        # การตั้งค่า UI
        self.ui_colors = {
            "primary": "#3498db",
            "success": "#2ecc71",
            "danger": "#e74c3c",
            "warning": "#f39c12",
            "background": "#f5f5f5",
        }

        self.config_file = config_file
        if config_file:
            self.load_from_file(config_file)

    def load_from_file(self, filename):
        """โหลดการตั้งค่าจากไฟล์ JSON"""
        try:
            with open(filename, "r", encoding="utf-8") as file:
                config_data = json.load(file)

            for key, value in config_data.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            print("Configuration loaded successfully.")
            return True
        except FileNotFoundError:
            print("Config file not found. Using default settings.")
            return False
        except Exception as e:
            print(f"Error loading config: {e}")
            return False

    def save_to_file(self, filename):
        """บันทึกการตั้งค่าลงไฟล์ JSON"""
        try:
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

            with open(filename, "w", encoding="utf-8") as file:
                json.dump(config_data, file, indent=4)
            print("Configuration saved successfully.")
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False


# ตัวอย่างการใช้งาน
config = BotConfig("config.json")
config.save_to_file("config.json")  # บันทึกค่าการตั้งค่าไปที่ไฟล์
