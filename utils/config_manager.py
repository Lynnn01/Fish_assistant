import json
import os
import time
from utils.constants import DEFAULT_CONFIG



class ConfigManager:
    """จัดการการตั้งค่าและการอัปเดตแอพพลิเคชัน"""

    def __init__(self, config_file="config.json"):
        """
        สร้างตัวจัดการการตั้งค่า

        Args:
            config_file: ที่อยู่ของไฟล์ config.json
        """
        self.config_file = config_file
        self.config = self.load_config()
        self.observers = []  # รายการคอลแบ็กสำหรับการแจ้งเตือนเมื่อการตั้งค่าเปลี่ยน

        # ตรวจสอบเวลาแก้ไขไฟล์ล่าสุด
        self.last_modified = self._get_file_modified_time()

    def load_config(self):
        """โหลดการตั้งค่าจากไฟล์ config.json"""
        try:
            with open(self.config_file, "r") as f:
                config = json.load(f)
                # ตรวจสอบและเพิ่มค่าที่ขาดหายไป
                self._verify_and_update_config(config)
                return config
        except (FileNotFoundError, json.JSONDecodeError):
            # ถ้าไฟล์ไม่มีหรือมีปัญหา ใช้ค่าเริ่มต้น
            self.save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG.copy()

    def _verify_and_update_config(self, config):
        """ตรวจสอบว่ามีค่าที่จำเป็นทั้งหมดหรือไม่ ถ้าไม่มีให้เพิ่มจากค่า default"""
        updated = False

        # ตรวจสอบค่าหลัก
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value
                updated = True
            elif key == "ui_colors" and isinstance(value, dict):
                # ตรวจสอบค่าสีย่อย
                if not isinstance(config[key], dict):
                    config[key] = value
                    updated = True
                else:
                    for color_key, color_value in value.items():
                        if color_key not in config[key]:
                            config[key][color_key] = color_value
                            updated = True

        # บันทึกการเปลี่ยนแปลงถ้ามีการอัปเดต
        if updated:
            self.save_config(config)

        return config

    def save_config(self, config=None):
        """บันทึกการตั้งค่าลงไฟล์ config.json

        Args:
            config: ข้อมูลการตั้งค่าที่จะบันทึก (หากไม่ระบุจะใช้ค่าปัจจุบัน)

        Returns:
            bool: True ถ้าบันทึกสำเร็จ, False ถ้าล้มเหลว
        """
        if config is None:
            config = self.config
        else:
            self.config = config

        try:
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=4)

            # อัปเดตเวลาแก้ไขล่าสุด
            self.last_modified = self._get_file_modified_time()

            # แจ้งเตือนผู้สังเกตการณ์ทุกรายการ
            self._notify_observers()

            return True
        except Exception as e:
            print(f"ไม่สามารถบันทึก config ได้: {e}")
            return False

    def _get_file_modified_time(self):
        """รับเวลาแก้ไขล่าสุดของไฟล์ config"""
        try:
            return os.path.getmtime(self.config_file)
        except FileNotFoundError:
            return 0

    def check_for_changes(self):
        """ตรวจสอบว่าไฟล์ config ถูกแก้ไขหรือไม่

        Returns:
            bool: True ถ้ามีการเปลี่ยนแปลง, False ถ้าไม่มี
        """
        current_modified = self._get_file_modified_time()
        if current_modified > self.last_modified:
            # โหลดการตั้งค่าใหม่
            self.config = self.load_config()
            self.last_modified = current_modified
            # แจ้งเตือนผู้สังเกตการณ์
            self._notify_observers()
            return True
        return False

    def get_value(self, key, default_value=None):
        """รับค่าจากการตั้งค่า

        Args:
            key: คีย์ที่ต้องการ
            default_value: ค่าเริ่มต้นที่จะใช้ถ้าไม่พบคีย์

        Returns:
            ค่าของคีย์ที่กำหนด หรือค่าเริ่มต้นถ้าไม่พบ
        """
        return self.config.get(key, default_value)

    def set_value(self, key, value):
        """ตั้งค่าและบันทึกลงไฟล์ config

        Args:
            key: คีย์ที่ต้องการตั้งค่า
            value: ค่าที่ต้องการกำหนด

        Returns:
            bool: True ถ้าบันทึกสำเร็จ, False ถ้าล้มเหลว
        """
        self.config[key] = value
        return self.save_config()

    def get_colors(self):
        """รับค่าสีทั้งหมดจากการตั้งค่า

        Returns:
            dict: dictionary ของสีทั้งหมด
        """
        return self.config.get("ui_colors", DEFAULT_CONFIG["ui_colors"])

    def register_observer(self, callback):
        """ลงทะเบียนฟังก์ชันที่จะเรียกเมื่อมีการเปลี่ยนแปลงการตั้งค่า

        Args:
            callback: ฟังก์ชันที่จะเรียกเมื่อมีการเปลี่ยนแปลง
        """
        if callback not in self.observers:
            self.observers.append(callback)

    def unregister_observer(self, callback):
        """ยกเลิกการลงทะเบียนฟังก์ชันผู้สังเกตการณ์

        Args:
            callback: ฟังก์ชันที่จะยกเลิก
        """
        if callback in self.observers:
            self.observers.remove(callback)

    def _notify_observers(self):
        """แจ้งเตือนผู้สังเกตการณ์ทุกรายการเกี่ยวกับการเปลี่ยนแปลง"""
        for callback in self.observers:
            try:
                callback(self.config)
            except Exception as e:
                print(f"เกิดข้อผิดพลาดในการแจ้งเตือนผู้สังเกตการณ์: {e}")
