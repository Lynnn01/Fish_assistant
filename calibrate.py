import time
import numpy as np
import pyautogui
import cv2
from PIL import ImageGrab
import keyboard


def calibrate(self):
    print("กำลังปรับเทียบ... กรุณาเตรียมหน้าต่างเกมให้พร้อม")
    print("กด 'c' เมื่อเกจวัดปรากฏบนหน้าจอ")

    while keyboard.is_pressed("c"):
        time.sleep(0.1)
    while not keyboard.is_pressed("c"):
        time.sleep(0.1)

    print("กำลังจับภาพหน้าจอ...")

    screenshot = np.array(ImageGrab.grab())

    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    cv2.imwrite("screenshot/screen_capture.png", screenshot)
    print("บันทึกภาพหน้าจอแล้วที่ screen_capture.png")

    left_pos, right_pos = position()
    gauge_width = right_pos[0] - left_pos[0]

    

    return left_pos, right_pos, gauge_width


def position():
    print("กรุณาเลือกบริเวณของเกจวัด:")
    print("เลื่อนเมาส์ไปที่ด้านซ้ายของเกจวัดและกด 'x'")

    while keyboard.is_pressed("x"):
        time.sleep(0.1)
    while not keyboard.is_pressed("x"):
        time.sleep(0.1)

    left_pos = pyautogui.position()
    print(f"ตำแหน่งซ้าย: {left_pos}")

    while keyboard.is_pressed("x"):
        time.sleep(0.1)

    print("เลื่อนเมาส์ไปที่ด้านขวาของเกจวัดและกด 'x'")
    while not keyboard.is_pressed("x"):
        time.sleep(0.1)

    right_pos = pyautogui.position()
    print(f"ตำแหน่งขวา: {right_pos}")

    while keyboard.is_pressed("x"):
        time.sleep(0.1)

    return left_pos, right_pos
