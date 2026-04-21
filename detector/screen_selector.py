import tkinter as tk
from PIL import Image, ImageTk
import pyautogui


def select_region(root, callback):
    """
    เปิดหน้าต่างเลือกพื้นที่แบบ fullscreen ด้วย tkinter
    เมื่อเลือกเสร็จจะเรียก callback(region) โดย region = (x1,y1,x2,y2) หรือ None
    """
    screenshot = pyautogui.screenshot()

    overlay = tk.Toplevel(root)
    overlay.attributes("-fullscreen", True)
    overlay.attributes("-topmost", True)
    overlay.configure(cursor="crosshair")
    overlay.lift()
    overlay.focus_force()

    screen_w = overlay.winfo_screenwidth()
    screen_h = overlay.winfo_screenheight()

    # แปลงภาพหน้าจอเป็น PhotoImage
    screenshot = screenshot.resize((screen_w, screen_h), Image.NEAREST)
    bg_image = ImageTk.PhotoImage(screenshot)

    canvas = tk.Canvas(
        overlay,
        width=screen_w,
        height=screen_h,
        highlightthickness=0,
        cursor="crosshair",
    )
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, anchor="nw", image=bg_image)
    canvas._bg_image = bg_image  # ป้องกัน GC เก็บ reference

    # overlay สีเข้มกึ่งโปร่งแสง
    canvas.create_rectangle(
        0, 0, screen_w, screen_h, fill="black", stipple="gray50", outline=""
    )

    # ข้อความคำแนะนำ
    instruction = canvas.create_text(
        screen_w // 2,
        40,
        text="คลิกมุมซ้ายบน ของพื้นที่เกจ  |  ESC = ยกเลิก",
        fill="#00ff00",
        font=("Courier", 18, "bold"),
    )

    state = {"start": None, "rect": None}

    def on_press(event):
        state["start"] = (event.x, event.y)
        if state["rect"]:
            canvas.delete(state["rect"])
        canvas.itemconfig(instruction, text="คลิกมุมขวาล่าง ของพื้นที่เกจ  |  ESC = ยกเลิก")

    def on_drag(event):
        if state["start"] is None:
            return
        if state["rect"]:
            canvas.delete(state["rect"])
        x0, y0 = state["start"]
        state["rect"] = canvas.create_rectangle(
            x0, y0, event.x, event.y, outline="#00ff00", width=2, dash=(6, 3)
        )

    def on_release(event):
        if state["start"] is None:
            return
        x1, y1 = state["start"]
        x2, y2 = event.x, event.y
        overlay.destroy()
        region = (
            min(x1, x2),
            min(y1, y2),
            max(x1, x2),
            max(y1, y2),
        )
        callback(
            region if region[2] - region[0] > 5 and region[3] - region[1] > 5 else None
        )

    def on_cancel(event=None):
        overlay.destroy()
        callback(None)

    canvas.bind("<ButtonPress-1>", on_press)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)
    overlay.bind("<Escape>", on_cancel)
