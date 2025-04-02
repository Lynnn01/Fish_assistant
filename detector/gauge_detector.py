import numpy as np
import pyautogui
import cv2
import time
from utils.constants import DEFAULT_CONFIG


class GaugeDetector:
    def __init__(self, app):
        self.app = app

        # ตั้งค่าเริ่มต้นด้วยค่า DEFAULT_CONFIG
        self.config = DEFAULT_CONFIG.copy()

        # ตัวแปรควบคุมการคลิก
        self.last_action_time = time.time()

    def update_config(self):
        """อัปเดตค่าการตั้งค่าจาก app.config_manager หากมี"""
        try:
            if (
                hasattr(self.app, "config_manager")
                and self.app.config_manager is not None
            ):
                # ตรวจสอบและอัปเดตค่าที่จำเป็น
                for key in DEFAULT_CONFIG:
                    if key in self.app.config_manager.config:
                        self.config[key] = self.app.config_manager.config[key]
            elif hasattr(self.app, "config") and self.app.config is not None:
                # ใช้ app.config แบบเดิมหากไม่มี config_manager
                for key in DEFAULT_CONFIG:
                    if hasattr(self.app.config, key):
                        self.config[key] = getattr(self.app.config, key)
        except Exception as e:
            print(f"Error updating config: {e}")
            # ในกรณีที่เกิดข้อผิดพลาด ใช้ค่า DEFAULT_CONFIG

    def detect_color_zone(self, image, line_x, region_y):
        """ตรวจสอบว่าตำแหน่งที่กำหนดอยู่ในโซนสีใด (แดง/เขียว)"""
        try:
            # ตรวจสอบว่าตำแหน่งอยู่ในขอบเขตของภาพ
            h, w = image.shape[:2]
            if line_x < 0 or line_x >= w or region_y < 0 or region_y >= h:
                return "unknown"

            # ดึงค่าสีที่ตำแหน่งนั้น
            color = image[region_y, line_x]  # [B, G, R]

            # ตรวจสอบว่ามีองค์ประกอบสีเขียวสูงกว่าอย่างชัดเจน
            if color[1] > 1.5 * max(color[0], color[2]) and color[1] > 100:
                return "green"

            # ตรวจสอบว่ามีองค์ประกอบสีแดงสูงกว่าอย่างชัดเจน
            if color[2] > 1.5 * max(color[0], color[1]) and color[2] > 100:
                return "red"

            return "unknown"
        except Exception as e:
            print(f"Error in detect_color_zone: {e}")
            return "unknown"

    def find_white_line(self, image):
        """หาตำแหน่งของเส้นขาวแนวตั้ง"""
        try:
            # แปลงเป็นโทนสีเทา
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # ใช้ค่า line_threshold จากการตั้งค่า
            line_threshold = self.config.get(
                "line_threshold", DEFAULT_CONFIG["line_threshold"]
            )

            # หาเส้นขาว
            _, thresh = cv2.threshold(gray, line_threshold, 255, cv2.THRESH_BINARY)

            # หาตำแหน่งของเส้นแนวตั้ง (คอลัมน์ที่มีพิกเซลสีขาวเยอะที่สุด)
            column_sum = np.sum(thresh, axis=0)

            if np.max(column_sum) > 0:
                # คืนค่าตำแหน่ง x ที่มีผลรวมสูงสุด
                return np.argmax(column_sum)

            return None
        except Exception as e:
            print(f"Error in find_white_line: {e}")
            return None

    def check_gauge_components(self, image):
        """ตรวจสอบองค์ประกอบของเกจ (เส้นขาว, โซนสีเขียว, โซนสีแดง)"""
        try:
            h, w = image.shape[:2]

            # 1. หาเส้นขาว
            white_line_x = self.find_white_line(image)
            if white_line_x is None:
                return None, False, False

            # 2. ตรวจหาสีเขียวและสีแดงในภาพ
            y_middle = h // 2

            found_green = False
            found_red = False

            # สุ่มตรวจสอบจุดต่างๆ ในแนวนอนเพื่อระบุโซนสี
            step = max(1, w // 20)  # แบ่งเป็น 20 ส่วน

            for x in range(0, w, step):
                zone = self.detect_color_zone(image, x, y_middle)

                if zone == "green":
                    found_green = True
                elif zone == "red":
                    found_red = True

                # หากพบทั้งสองสีแล้ว ไม่จำเป็นต้องตรวจสอบเพิ่ม
                if found_green and found_red:
                    break

            return white_line_x, found_green, found_red
        except Exception as e:
            print(f"Error in check_gauge_components: {e}")
            return None, False, False

    def get_gauge_zone(self, relative_pos):
        """ระบุว่าตำแหน่งในเกจอยู่ในโซนใด"""
        # อัปเดตค่าจากการตั้งค่า
        red_zone_threshold = self.config.get(
            "red_zone_threshold", DEFAULT_CONFIG["red_zone_threshold"]
        )
        buffer_zone_size = self.config.get(
            "buffer_zone_size", DEFAULT_CONFIG["buffer_zone_size"]
        )

        # คำนวณขอบเขตของโซน
        safe_zone_min = red_zone_threshold + buffer_zone_size
        safe_zone_max = 1.0 - red_zone_threshold - buffer_zone_size

        # ระบุโซน
        if relative_pos < red_zone_threshold:
            return "danger_left", "LEFT DANGER - Clicking!"
        elif relative_pos < safe_zone_min:
            return "caution_left", "LEFT CAUTION - Clicking!"
        elif relative_pos > (1.0 - red_zone_threshold):
            return "danger_right", "RIGHT DANGER - Stop Clicking!"
        elif relative_pos > safe_zone_max:
            return "caution_right", "RIGHT CAUTION - Stop Clicking!"
        else:
            return "safe", "SAFE ZONE - Clicking!"

    def fishing_loop(self, region, ui):
        """การทำงานหลักสำหรับตรวจจับและคลิก"""
        if not region:
            return

        x1, y1, x2, y2 = region
        gauge_width = x2 - x1

        # ตัวแปรติดตามสถานะ
        last_line_detected_time = time.time()
        gauge_was_detected = False
        last_missing_gauge_click_time = 0

        while self.app.running:
            try:
                # อัปเดตค่าจากการตั้งค่า
                self.update_config()

                # จับภาพหน้าจอ
                screenshot = pyautogui.screenshot(region=(x1, y1, x2 - x1, y2 - y1))
                screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

                # ตรวจสอบองค์ประกอบของเกจ
                white_line_x, found_green, found_red = self.check_gauge_components(
                    screenshot_cv
                )

                current_time = time.time()

                # พบเกจสมบูรณ์ (มีทั้งเส้นขาว, โซนสีเขียว, โซนสีแดง)
                if white_line_x is not None and found_green and found_red:
                    # คำนวณตำแหน่งสัมพัทธ์
                    relative_pos = white_line_x / gauge_width

                    # พบเกจที่สมบูรณ์
                    gauge_was_detected = True
                    last_line_detected_time = current_time

                    # อัปเดตตำแหน่งและสถานะ
                    ui.update_line_position(relative_pos)

                    # ระบุโซนและดำเนินการตามโซน
                    zone, status_text = self.get_gauge_zone(relative_pos)

                    # กำหนดการคลิกตามโซน
                    should_click = zone in ["safe", "caution_left", "danger_left"]

                    if should_click:
                        # ใช้ค่า action_cooldown จากการตั้งค่า
                        action_cooldown = self.config.get(
                            "action_cooldown", DEFAULT_CONFIG["action_cooldown"]
                        )

                        if current_time - self.last_action_time > action_cooldown:
                            pyautogui.click()
                            self.last_action_time = current_time
                            ui.update_status(
                                status_text, "success" if zone == "safe" else "warning"
                            )
                    else:
                        ui.update_status(status_text, "danger")

                # พบเส้นขาวแต่ไม่พบสีอื่น - เกจไม่สมบูรณ์
                elif white_line_x is not None:
                    ui.update_status("Incomplete gauge detected", "warning")

                    # คลิกตามรอบเวลาที่กำหนด
                    periodic_click_interval = self.config.get(
                        "periodic_click_interval",
                        DEFAULT_CONFIG["periodic_click_interval"],
                    )

                    if (
                        current_time - last_missing_gauge_click_time
                        >= periodic_click_interval
                    ):
                        pyautogui.click()
                        last_missing_gauge_click_time = current_time
                        ui.update_status(
                            f"Incomplete gauge - Clicking every {periodic_click_interval}s",
                            "warning",
                        )

                # ไม่พบเส้นขาว - เกจหายไป
                else:
                    ui.update_status("No gauge detected", "warning")

                    # คลิกหากเกจหายไป และเคยพบเกจมาก่อน
                    if gauge_was_detected:
                        first_click_delay = self.config.get(
                            "first_click_delay", DEFAULT_CONFIG["first_click_delay"]
                        )
                        periodic_click_interval = self.config.get(
                            "periodic_click_interval",
                            DEFAULT_CONFIG["periodic_click_interval"],
                        )

                        if current_time - last_line_detected_time >= first_click_delay:
                            if (
                                current_time - last_missing_gauge_click_time
                                >= periodic_click_interval
                            ):
                                pyautogui.click()
                                last_missing_gauge_click_time = current_time
                                ui.update_status(
                                    f"No gauge - Clicking every {periodic_click_interval}s",
                                    "warning",
                                )

                # หน่วงเวลาเล็กน้อย
                time.sleep(0.01)

            except Exception as e:
                print(f"Error in fishing loop: {e}")
                ui.update_status(f"Error: {str(e)[:20]}...", "danger")
                time.sleep(1)
