import numpy as np
import pyautogui
import cv2
import time


class GaugeDetector:
    def __init__(self, app):
        self.app = app
        self.config = app.config  # ใช้การตั้งค่าจาก app

        # นำค่าจาก config มาใช้
        self.red_zone_threshold = self.config.red_zone_threshold
        self.buffer_zone_size = self.config.buffer_zone_size
        self.line_threshold = self.config.line_threshold
        self.color_threshold = self.config.color_threshold

        # ตัวแปรควบคุมการคลิก
        self.last_action_time = time.time()
        self.action_cooldown = self.config.action_cooldown

    def detect_color_region(self, image, line_x, region_y):
        """ตรวจสอบว่าเส้นขาวอยู่ในโซนสีใด"""
        try:
            color = image[region_y, line_x]  # [B, G, R]

            # กำหนดค่าสีที่ต้องการตรวจจับ (BGR format)
            green_target = np.array([83, 250, 83])
            red_target = np.array([76, 98, 251])

            # คำนวณระยะห่างของสี (ยิ่งน้อยยิ่งใกล้เคียง)
            green_distance = np.sum(np.abs(color.astype(np.int32) - green_target))
            red_distance = np.sum(np.abs(color.astype(np.int32) - red_target))

            # กำหนดค่าเกณฑ์ (threshold) สำหรับความใกล้เคียงของสี
            color_threshold = 150  # ปรับค่านี้ตามความเหมาะสม

            # ตรวจสอบว่าใกล้เคียงกับสีเขียวหรือสีแดง
            if green_distance < color_threshold and green_distance < red_distance:
                return "green"
            elif red_distance < color_threshold and red_distance < green_distance:
                return "red"

            return "other"
        except Exception as e:
            print(f"Error in detect_color_region: {e}")
            return "other"

    def find_white_line(self, image, start_y, end_y, region_x_min, region_x_max):
        """หาตำแหน่งของเส้นขาวแนวตั้ง"""
        # ดึงภาพในพื้นที่ที่สนใจ
        roi = image[start_y:end_y, region_x_min:region_x_max]

        # แปลงเป็นโทนสีเทา
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        # หาเส้นขาว
        _, thresh = cv2.threshold(gray, self.line_threshold, 255, cv2.THRESH_BINARY)

        # หาตำแหน่งของเส้นขาว
        column_sum = np.sum(thresh, axis=0)
        if np.max(column_sum) > 0:
            line_x_local = np.argmax(column_sum)
            line_x_global = line_x_local + region_x_min
            return line_x_global

        return None

    def fishing_loop(self, region, ui):
        """การทำงานหลักสำหรับตรวจจับและคลิก"""
        if not region:
            return

        x1, y1, x2, y2 = region
        gauge_width = x2 - x1
        gauge_height = y2 - y1

        # โซนที่ปลอดภัยสำหรับคลิก
        safe_zone_min = self.red_zone_threshold + self.buffer_zone_size
        safe_zone_max = 1.0 - self.red_zone_threshold - self.buffer_zone_size

        # ตัวแปรติดตามเวลาที่เกจหายไป
        last_line_detected_time = time.time()
        gauge_was_detected = False  # เพื่อติดตามว่าเคยตรวจพบเกจมาก่อนหรือไม่
        last_missing_gauge_click_time = 0  # เวลาล่าสุดที่คลิกหลังจากเกจหาย

        while self.app.running:
            try:
                # จับภาพหน้าจอ
                screenshot = pyautogui.screenshot(region=(x1, y1, x2 - x1, y2 - y1))
                screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

                # หาเส้นขาว
                white_line_x_local = self.find_white_line(
                    screenshot_cv, 0, gauge_height, 0, gauge_width
                )

                current_time = time.time()

                # ตรวจสอบว่าพบเส้นขาวหรือไม่
                if white_line_x_local is not None:
                    # พบเส้นขาว ตรวจสอบเพิ่มเติมว่ามีสีเขียวและสีแดงด้วยหรือไม่

                    # คำนวณตำแหน่งของเส้นขาวเทียบกับความกว้างของเกจ
                    relative_pos = white_line_x_local / gauge_width

                    # ตรวจสอบโซนสีต่างๆ ในเกจ
                    found_green = False
                    found_red = False

                    # ตรวจหาสีเขียวและสีแดงในภาพ
                    check_y = gauge_height // 2

                    # ตรวจสอบทุกจุดในแนวนอนเพื่อหาสีเขียวและสีแดง
                    for test_x in range(
                        0, gauge_width, 5
                    ):  # ข้ามทุกๆ 5 พิกเซลเพื่อลดการประมวลผล
                        color = self.detect_color_region(screenshot_cv, test_x, check_y)
                        if color == "green":
                            found_green = True
                        elif color == "red":
                            found_red = True

                        # ถ้าพบทั้งสีเขียวและสีแดงแล้ว ให้หยุดการค้นหา
                        if found_green and found_red:
                            break

                    # ถ้าพบครบทุกองค์ประกอบ (ขาว เขียว แดง)
                    if found_green and found_red:
                        # พบเกจที่สมบูรณ์
                        gauge_was_detected = True
                        last_line_detected_time = current_time

                        # อัปเดตตำแหน่งเส้นในเกจ
                        ui.update_line_position(relative_pos)

                        # ตรวจสอบว่าอยู่ในโซนปลอดภัยหรือไม่
                        in_safe_zone = safe_zone_min <= relative_pos <= safe_zone_max

                        # อยู่ใกล้โซนแดงซ้ายหรือขวา
                        near_left_red = relative_pos < safe_zone_min
                        near_right_red = relative_pos > safe_zone_max

                        # ตรรกะการคลิก
                        if in_safe_zone:
                            # อยู่ในโซนปลอดภัย - คลิกได้
                            if (
                                current_time - self.last_action_time
                                > self.action_cooldown
                            ):
                                pyautogui.click()
                                self.last_action_time = current_time
                                ui.update_status("SAFE - Clicking!", "success")

                        elif near_left_red:
                            # ใกล้โซนแดงซ้าย - คลิกต่อ
                            if (
                                current_time - self.last_action_time
                                > self.action_cooldown
                            ):
                                pyautogui.click()
                                self.last_action_time = current_time
                                ui.update_status("NEAR LEFT RED - Clicking!", "warning")

                        elif near_right_red:
                            # ใกล้โซนแดงขวา - หยุดคลิก
                            ui.update_status(
                                "NEAR RIGHT RED - Stop Clicking!", "danger"
                            )
                    else:
                        # พบเส้นขาวแต่ไม่พบสีเขียวหรือสีแดง ถือว่าไม่พบเกจที่สมบูรณ์
                        ui.update_status("Incomplete gauge detected", "warning")

                        # กดทุก 4 วินาที
                        if current_time - last_missing_gauge_click_time >= 4.5:
                            pyautogui.click()
                            last_missing_gauge_click_time = current_time
                            ui.update_status(
                                "Incomplete gauge - Clicking every 4s", "warning"
                            )
                else:
                    # ไม่พบเส้นขาว
                    ui.update_status("No line detected", "warning")

                    # กดทุก 4 วินาที ถ้าเคยพบเกจมาก่อน
                    if gauge_was_detected and (
                        current_time - last_line_detected_time >= 1.0
                    ):
                        if current_time - last_missing_gauge_click_time >= 4.5:
                            pyautogui.click()
                            last_missing_gauge_click_time = current_time
                            ui.update_status("No gauge - Clicking every 4s", "warning")

                # หน่วงเวลาเล็กน้อยเพื่อลดการใช้ CPU
                time.sleep(0.01)

            except Exception as e:
                print(f"Error in fishing loop: {e}")
                ui.update_status(f"Error: {str(e)[:20]}...", "danger")
                time.sleep(1)
