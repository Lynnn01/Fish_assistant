import time
import numpy as np
import pyautogui
import cv2
from PIL import ImageGrab
import keyboard
from calibrate import calibrate


class FishingBot:
    def __init__(self):
        # ตั้งค่าพารามิเตอร์
        self.screen_region = None  # จะถูกกำหนดระหว่างการปรับเทียบ
        self.gauge_y_position = None  # ตำแหน่ง Y ของเกจวัด
        self.green_hsv_lower = np.array([40, 100, 100])  # ช่วง HSV ต่ำสุดของสีเขียว
        self.green_hsv_upper = np.array([80, 255, 255])  # ช่วง HSV สูงสุดของสีเขียว

        # ตัวแปรขณะทำงาน
        self.running = False
        self.debug_mode = False


if __name__ == "__main__":
    bot = FishingBot()
    print("ยินดีต้อนรับสู่บอทตกปลา!")
    print("1. กด 'c' เพื่อปรับเทียบตำแหน่งเกจวัด")
    print("2. กด 's' เพื่อเริ่มการทำงานของบอท")
    print("3. กด 'q' เพื่อออกจากโปรแกรม")

    while True:
        if keyboard.is_pressed("q"):
            print("กำลังออกจากโปรแกรม...")
            break

        elif keyboard.is_pressed("c"):
            left_pos, right_pos, gauge_width = calibrate(bot)

            bot.screen_region = (
                left_pos[0] - 10,  # x เริ่มต้น
                left_pos[1] - 20,  # y เริ่มต้น
                right_pos[0] + 10,  # x สิ้นสุด
                left_pos[1] + 20,  # y สิ้นสุด
            )

            bot.gauge_y_position = left_pos[1] - 10  # ตำแหน่ง Y ของเกจวัด
            print(f"ปรับเทียบเสร็จสิ้น: บริเวณเกจวัด = {bot.screen_region}")
