import numpy as np
import pyautogui
import cv2
import time
import keyboard
import os
import threading
from PIL import Image, ImageTk


class FishingDetector:
    def __init__(self, app):
        self.app = app
        self.ui = app.ui  # Reference to UI

        # การตั้งค่าเริ่มต้น
        self.region = None
        self.is_clicking = False
        self.last_action_time = time.time()
        self.last_catch_time = time.time()
        self.action_cooldown = 0.1
        self.catch_cooldown = 0.5

        # อ่านค่าการตั้งค่าจาก config
        self.update_settings_from_config(app.config)

        # ตัวแปรสำหรับตรวจจับ
        self.detected_area_image = None
        self.detection_history = []
        self.debug_mode = False

    def update_settings_from_config(self, config):
        """อัปเดตการตั้งค่าจาก config"""
        # Color Sensitivity
        self.green_tolerance = config.get("green_tolerance", 30)

        # Line Detection
        self.line_threshold = config.get("line_threshold", 200)

        # Click Settings
        self.action_cooldown = config.get("action_cooldown", 0.1)
        self.catch_cooldown = config.get("catch_cooldown", 0.5)

        # Advanced Settings
        self.double_click = config.get("double_click", False)
        self.double_click_delay = config.get("double_click_delay", 0.1)
        self.auto_restart = config.get("auto_restart", False)
        self.green_color = self.parse_rgba(
            config.get("green_color", "rgba(83,250,83,255)")
        )
        self.red_color = self.parse_rgba(config.get("red_color", "rgba(251,98,76,255)"))
        self.white_color = self.parse_rgba(
            config.get("white_color", "rgba(255,255,255,255)")
        )

    def parse_rgba(self, rgba_str):
        """แปลงค่า rgba string เป็น tuple (B,G,R)"""
        # รูปแบบ rgba(r,g,b,a)
        parts = rgba_str.strip()[5:-1].split(",")
        r = int(parts[0])
        g = int(parts[1])
        b = int(parts[2])
        return (b, g, r)  # OpenCV ใช้รูปแบบ BGR

    def select_gauge_region(self):
        """เลือกพื้นที่ตรวจจับเกจ"""
        self.app.root.iconify()  # Minimize main window
        time.sleep(0.5)  # Wait for window to minimize

        # Take a screenshot
        screenshot = pyautogui.screenshot()
        screenshot_np = np.array(screenshot)
        screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

        # Create a selection window
        cv2.namedWindow("Select Gauge Region", cv2.WINDOW_NORMAL)

        # Variables to store selection
        region_points = []

        def mouse_callback(event, x, y, flags, param):
            nonlocal region_points, screenshot_cv

            if event == cv2.EVENT_LBUTTONDOWN:
                if len(region_points) < 2:
                    region_points.append((x, y))

                    # ถ้าเลือกจุดแรก
                    if len(region_points) == 1:
                        # วาดเส้นแนวนอนและแนวตั้งผ่านตำแหน่งเมาส์
                        temp_img = screenshot_cv.copy()
                        cv2.line(
                            temp_img, (0, y), (temp_img.shape[1], y), (0, 255, 0), 1
                        )
                        cv2.line(
                            temp_img, (x, 0), (x, temp_img.shape[0]), (0, 255, 0), 1
                        )
                        cv2.circle(temp_img, (x, y), 5, (0, 0, 255), -1)
                        cv2.imshow("Select Gauge Region", temp_img)

                    if len(region_points) == 2:
                        cv2.destroyAllWindows()

        cv2.setMouseCallback("Select Gauge Region", mouse_callback)

        # Display instructions
        instruction_img = screenshot_cv.copy()
        cv2.putText(
            instruction_img,
            "Click on the top-left and bottom-right corners of the gauge area",
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2,
        )
        cv2.imshow("Select Gauge Region", instruction_img)

        while len(region_points) < 2:
            display_img = screenshot_cv.copy()

            # Draw points selected
            for point in region_points:
                cv2.circle(display_img, point, 5, (0, 0, 255), -1)

            # ถ้ามีจุดแรกแล้วให้แสดงกรอบพื้นที่ที่กำลังจะเลือก
            if len(region_points) == 1:
                # ดึงพิกัดเมาส์ปัจจุบัน
                mouse_x, mouse_y = pyautogui.position()
                # วาดกรอบสี่เหลี่ยมจากจุดแรกถึงเมาส์ปัจจุบัน
                cv2.rectangle(
                    display_img, region_points[0], (mouse_x, mouse_y), (0, 255, 0), 2
                )

            cv2.imshow("Select Gauge Region", display_img)

            if cv2.waitKey(1) == 27:  # ESC key
                region_points = []
                cv2.destroyAllWindows()
                break

        # Restore main window
        self.app.root.deiconify()

        # Process the selected region
        if len(region_points) == 2:
            x1 = min(region_points[0][0], region_points[1][0])
            y1 = min(region_points[0][1], region_points[1][1])
            x2 = max(region_points[0][0], region_points[1][0])
            y2 = max(region_points[0][1], region_points[1][1])

            self.region = (x1, y1, x2, y2)
            self.ui.update_region_info(self.region)
            self.ui.update_status("Region selected", "warning")
            self.ui.set_button_states(select=True, start=True, stop=False)

            # บันทึกภาพตัวอย่างของพื้นที่ที่เลือก
            self.capture_region_sample()

            return True
        return False

    def capture_region_sample(self):
        """จับภาพตัวอย่างของพื้นที่ที่เลือก"""
        if self.region:
            x1, y1, x2, y2 = self.region
            # จับภาพหน้าจอ
            screenshot = pyautogui.screenshot(region=(x1, y1, x2 - x1, y2 - y1))
            # แปลงเป็น numpy array
            self.detected_area_image = np.array(screenshot)
            # แปลงเป็น BGR (สำหรับ OpenCV)
            self.detected_area_image = cv2.cvtColor(
                self.detected_area_image, cv2.COLOR_RGB2BGR
            )

            # อัปเดต UI ด้วยภาพตัวอย่าง
            self.ui.update_sample_image(self.detected_area_image)

    def detect_color_region(self, image, line_x, region_y):
        """ตรวจสอบว่าเส้นขาวอยู่ในโซนสีใด"""
        color = image[region_y, line_x]  # [B, G, R]

        # เปรียบเทียบกับสีเขียวที่กำหนด
        green_b, green_g, green_r = self.green_color
        if (
            abs(color[0] - green_b) + abs(color[1] - green_g) + abs(color[2] - green_r)
        ) < self.green_tolerance * 3:
            return "green"

        # เปรียบเทียบกับสีแดงที่กำหนด
        red_b, red_g, red_r = self.red_color
        if (
            abs(color[0] - red_b) + abs(color[1] - red_g) + abs(color[2] - red_r)
        ) < self.green_tolerance * 3:
            return "red"

        # กรณีอื่นๆ
        return "other"

    def find_white_line(self, image, start_y, end_y, region_x_min, region_x_max):
        """หาตำแหน่ง x ของเส้นขาวแนวตั้ง"""
        # แยกส่วนภาพที่สนใจ
        roi = image[start_y:end_y, region_x_min:region_x_max]

        # แปลงเป็นโทนเทา
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        # Threshold เพื่อหาเส้นขาว
        _, thresh = cv2.threshold(gray, self.line_threshold, 255, cv2.THRESH_BINARY)

        # หาตำแหน่งของเส้นขาว
        column_sum = np.sum(thresh, axis=0)
        if np.max(column_sum) > 0:
            line_x_local = np.argmax(column_sum)
            line_x_global = line_x_local + region_x_min
            return line_x_global

        return None

    def fishing_loop(self):
        """การทำงานหลักสำหรับตรวจจับและคลิก"""
        if not self.region:
            return

        x1, y1, x2, y2 = self.region
        gauge_width = x2 - x1
        gauge_height = y2 - y1
        catch_count = 0
        total_checks = 0
        detection_rate = 0

        while self.app.running:
            try:
                # จับภาพหน้าจอ
                screenshot = pyautogui.screenshot(region=(x1, y1, x2 - x1, y2 - y1))
                screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

                # หาเส้นขาว
                white_line_x_local = self.find_white_line(
                    screenshot_cv, 0, gauge_height, 0, gauge_width
                )

                total_checks += 1

                if white_line_x_local is not None:
                    # คำนวณตำแหน่งจริงบนหน้าจอ
                    white_line_x = white_line_x_local + x1

                    # ตรวจสอบสีที่ตำแหน่ง y ที่เหมาะสม
                    check_y_local = gauge_height // 2
                    region_color = self.detect_color_region(
                        screenshot_cv, white_line_x_local, check_y_local
                    )

                    # เพิ่มประวัติการตรวจจับ
                    self.detection_history.append(region_color)
                    if len(self.detection_history) > 10:
                        self.detection_history.pop(0)

                    # อัปเดตอัตราการตรวจจับ
                    detection_rate = 100

                    # อัปเดตตำแหน่งเส้นในพรีวิว UI
                    relative_pos = white_line_x_local / gauge_width
                    self.ui.update_line_position(relative_pos)

                    if region_color == "green":
                        # คลิกถ้าอยู่ในโซนสีเขียวและผ่านช่วงเวลา cooldown
                        current_time = time.time()
                        if current_time - self.last_action_time > self.action_cooldown:
                            # ทำการคลิก
                            pyautogui.click()

                            # ถ้าเปิดใช้ double click
                            if self.double_click:
                                time.sleep(self.double_click_delay)
                                pyautogui.click()

                            self.last_action_time = current_time
                            self.is_clicking = True
                            self.ui.update_status("GREEN - Clicking!", "success")

                            # นับจำนวนปลาที่จับได้โดยมีการป้องกันการนับซ้ำในเวลาสั้นๆ
                            if (
                                current_time - self.last_catch_time
                                > self.catch_cooldown
                            ):
                                catch_count += 1
                                self.last_catch_time = current_time
                                self.ui.update_catch_counter(catch_count)

                                # เพิ่มสถิติ
                                self.app.analytics.add_catch()

                    elif region_color == "red":
                        self.is_clicking = False
                        self.ui.update_status("RED - Waiting...", "danger")

                    else:
                        self.is_clicking = False
                        self.ui.update_status("Monitoring...", "primary")

                else:
                    self.is_clicking = False
                    self.ui.update_status("No line detected", "inactive")

                    # อัปเดตอัตราการตรวจจับ
                    detection_rate = max(0, detection_rate - 5)  # ลดลงเรื่อยๆ

                    # ถ้าไม่พบเส้นเป็นเวลานาน และเปิดใช้ auto restart
                    if detection_rate == 0 and self.app.config.get(
                        "auto_restart", False
                    ):
                        self.ui.update_status("Auto-restarting fishing...", "warning")
                        # จำลองการกดปุ่มคีย์บอร์ดเพื่อเริ่มตกปลาใหม่
                        pyautogui.press(self.app.config.get("fishing_key", "e"))

                # อัปเดตอัตราการตรวจจับ
                self.ui.update_detection_rate(detection_rate)

                # อัปเดตภาพตัวอย่างถ้าอยู่ในโหมด debug
                if self.debug_mode and total_checks % 10 == 0:
                    self.ui.update_sample_image(screenshot_cv)

                # หน่วงเวลาเล็กน้อยเพื่อลดการใช้ CPU
                time.sleep(0.01)

            except Exception as e:
                print(f"Error in fishing loop: {e}")
                self.ui.update_status(f"Error: {str(e)[:20]}...", "danger")
                time.sleep(1)
