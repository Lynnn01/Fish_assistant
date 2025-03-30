import numpy as np
import pyautogui
import matplotlib.pyplot as plt
import keyboard
import os

# สร้างหน้าต่างแสดงผลและเก็บ reference
plt.figure()
img_plot = plt.imshow(np.array(pyautogui.screenshot()))
plt.axis("off")

try:
    while True:
        screenshot = pyautogui.screenshot()
        img_plot.set_data(np.array(screenshot))
        plt.draw()
        plt.pause(0.01)

        # ตรวจสอบการกดปุ่ม q เพื่อออก
        if keyboard.is_pressed("q"):
            print("Quit")
            break

        # ช่วยเคลียร์หน่วยความจำ
        del screenshot

finally:
    plt.close()
