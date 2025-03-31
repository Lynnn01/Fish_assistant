import numpy as np
import pyautogui
import cv2
import time


class GaugeDetector:
    def __init__(self, app):
        self.app = app

        # การตั้งค่าการตรวจจับ
        self.red_zone_threshold = 0.2  # ระยะห่างจากขอบที่ถือว่าเป็นโซนแดง
        self.buffer_zone_size = 0.125  # โซนกันชนก่อนถึงโซนแดง
        self.line_threshold = 200  # ความสว่างขั้นต่ำสำหรับเส้นขาว
        self.color_threshold = 30  # ความแตกต่างของสีขั้นต่ำ

        # ตั้งค่าการคลิก
        self.last_action_time = time.time()
        self.action_cooldown = 0.1

    def select_region(self, root_window):
        """เลือกพื้นที่ตรวจจับเกจ"""
        root_window.iconify()  # Minimize main window
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
        root_window.deiconify()

        # Process the selected region
        if len(region_points) == 2:
            x1 = min(region_points[0][0], region_points[1][0])
            y1 = min(region_points[0][1], region_points[1][1])
            x2 = max(region_points[0][0], region_points[1][0])
            y2 = max(region_points[0][1], region_points[1][1])

            return (x1, y1, x2, y2)

        return None

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
                        if current_time - last_missing_gauge_click_time >= 4.0:
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
                        if current_time - last_missing_gauge_click_time >= 4.0:
                            pyautogui.click()
                            last_missing_gauge_click_time = current_time
                            ui.update_status("No gauge - Clicking every 4s", "warning")

                # หน่วงเวลาเล็กน้อยเพื่อลดการใช้ CPU
                time.sleep(0.01)

            except Exception as e:
                print(f"Error in fishing loop: {e}")
                ui.update_status(f"Error: {str(e)[:20]}...", "danger")
                time.sleep(1)
