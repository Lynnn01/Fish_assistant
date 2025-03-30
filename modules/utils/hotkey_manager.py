import keyboard


class HotkeyManager:
    def __init__(self, app):
        self.app = app
        self.registered_hotkeys = {}

        # ลงทะเบียน Hotkey เริ่มต้น
        self.register_default_hotkeys()

    def register_default_hotkeys(self):
        """ลงทะเบียน hotkey ตามการตั้งค่า"""
        config = self.app.config

        # Hotkey หยุดการทำงาน
        stop_key = config.get("stop_hotkey", "f10")
        self.register_hotkey(stop_key, self.app.stop_fishing)

        # Hotkey เริ่มการทำงาน
        start_key = config.get("start_hotkey", "f6")
        self.register_hotkey(start_key, self.app.start_fishing)

    def register_hotkey(self, key, callback):
        """ลงทะเบียน hotkey ใหม่"""
        try:
            # ยกเลิกการลงทะเบียนเดิมถ้ามี
            if key in self.registered_hotkeys:
                keyboard.remove_hotkey(self.registered_hotkeys[key])

            # ลงทะเบียนใหม่
            hotkey_id = keyboard.add_hotkey(key, callback)
            self.registered_hotkeys[key] = hotkey_id
            return True
        except Exception as e:
            print(f"Error registering hotkey {key}: {e}")
            return False

    def unregister_hotkey(self, key):
        """ยกเลิกการลงทะเบียน hotkey"""
        if key in self.registered_hotkeys:
            try:
                keyboard.remove_hotkey(self.registered_hotkeys[key])
                del self.registered_hotkeys[key]
                return True
            except Exception as e:
                print(f"Error unregistering hotkey {key}: {e}")
        return False

    def unregister_all_hotkeys(self):
        """ยกเลิกการลงทะเบียน hotkey ทั้งหมด"""
        for key in list(self.registered_hotkeys.keys()):
            self.unregister_hotkey(key)
