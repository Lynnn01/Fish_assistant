import os
import json


class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.default_config = {
            # UI Settings
            "theme": "light",
            "animation_speed": 5,
            # Detection Settings
            "green_tolerance": 30,
            "line_threshold": 200,
            # Click Settings
            "action_cooldown": 0.1,
            "catch_cooldown": 0.5,
            "double_click": False,
            "double_click_delay": 0.1,
            # Color Settings
            "green_color": "rgba(83,250,83,255)",
            "red_color": "rgba(251,98,76,255)",
            "white_color": "rgba(255,255,255,255)",
            # Hotkeys
            "start_hotkey": "f6",
            "stop_hotkey": "f10",
            "fishing_key": "e",
            # Advanced Settings
            "auto_restart": False,
            "auto_start": False,
            "sound_alerts": True,
            "minimize_to_tray": False,
        }

    def load_config(self):
        """โหลดการตั้งค่าจากไฟล์ หรือสร้างใหม่ถ้าไม่มี"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    config = json.load(f)

                # รวมค่าเริ่มต้นกับค่าที่โหลด เพื่อให้แน่ใจว่ามีค่าครบทุกตัว
                merged_config = self.default_config.copy()
                merged_config.update(config)
                return merged_config
            else:
                # บันทึกไฟล์ default
                self.save_config(self.default_config)
                return self.default_config
        except Exception as e:
            print(f"Error loading config: {e}")
            return self.default_config

    def save_config(self, config):
        """บันทึกการตั้งค่าลงไฟล์"""
        try:
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
