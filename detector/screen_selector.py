import numpy as np
import pyautogui
import cv2
import time


def select_region(root_window):
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
                    cv2.line(temp_img, (0, y), (temp_img.shape[1], y), (0, 255, 0), 1)
                    cv2.line(temp_img, (x, 0), (x, temp_img.shape[0]), (0, 255, 0), 1)
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
