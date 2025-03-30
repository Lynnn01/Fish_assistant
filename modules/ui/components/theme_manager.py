import tkinter as tk
from tkinter import ttk


class ThemeManager:
    def __init__(self, ui, initial_theme="light"):
        self.ui = ui
        self.root = ui.root

        # ธีมที่มี
        self.themes = {
            "light": {
                "bg_color": "#f9f9f9",
                "text_color": "#2c3e50",
                "primary_color": "#3498db",
                "secondary_color": "#2ecc71",
                "warning_color": "#e74c3c",
                "accent_color": "#9b59b6",
                "border_color": "#dcdcdc",
            },
            "dark": {
                "bg_color": "#2c3e50",
                "text_color": "#ecf0f1",
                "primary_color": "#3498db",
                "secondary_color": "#2ecc71",
                "warning_color": "#e74c3c",
                "accent_color": "#9b59b6",
                "border_color": "#34495e",
            },
            "blue": {
                "bg_color": "#e8f4fc",
                "text_color": "#2c3e50",
                "primary_color": "#1a5276",
                "secondary_color": "#2ecc71",
                "warning_color": "#e74c3c",
                "accent_color": "#8e44ad",
                "border_color": "#aed6f1",
            },
            "green": {
                "bg_color": "#e9f7ef",
                "text_color": "#2c3e50",
                "primary_color": "#27ae60",
                "secondary_color": "#2980b9",
                "warning_color": "#e74c3c",
                "accent_color": "#8e44ad",
                "border_color": "#abebc6",
            },
        }

        # ตั้งค่าธีมเริ่มต้น
        self.current_theme = initial_theme
        self.apply_theme(initial_theme)

    def apply_theme(self, theme_name):
        """กำหนดธีมตามชื่อ"""
        if theme_name not in self.themes:
            theme_name = "light"  # ใช้ธีมเริ่มต้นถ้าไม่พบ

        # ดึงค่าสีจากธีมที่เลือก
        theme = self.themes[theme_name]

        # กำหนดตัวแปรสีสำหรับใช้ในคลาส
        for key, value in theme.items():
            setattr(self, key, value)

        # กำหนดสไตล์ ttk
        style = ttk.Style()

        # กำหนดสีพื้นหลัง
        style.configure("TFrame", background=self.bg_color)
        style.configure("TLabel", background=self.bg_color, foreground=self.text_color)
        style.configure(
            "TLabelframe", background=self.bg_color, foreground=self.text_color
        )
        style.configure(
            "TLabelframe.Label", background=self.bg_color, foreground=self.text_color
        )
        style.configure("TButton", background=self.bg_color, foreground=self.text_color)
        style.configure(
            "TCheckbutton", background=self.bg_color, foreground=self.text_color
        )
        style.configure(
            "TRadiobutton", background=self.bg_color, foreground=self.text_color
        )
        style.configure(
            "TEntry", fieldbackground=self.bg_color, foreground=self.text_color
        )
        style.configure(
            "TCombobox", fieldbackground=self.bg_color, foreground=self.text_color
        )

        # กำหนดสไตล์ปุ่มแบบกำหนดเอง
        style.configure(
            "Primary.TButton",
            background=self.primary_color,
            foreground="white",
            font=("Arial", 10, "bold"),
        )

        style.configure(
            "Success.TButton",
            background=self.secondary_color,
            foreground="white",
            font=("Arial", 10, "bold"),
        )

        style.configure(
            "Danger.TButton",
            background=self.warning_color,
            foreground="white",
            font=("Arial", 10, "bold"),
        )

        style.configure(
            "Accent.TButton",
            background=self.accent_color,
            foreground="white",
            font=("Arial", 10, "bold"),
        )

        # อัปเดตสีพื้นหลังหลัก
        self.root.configure(bg=self.bg_color)

        # อัปเดต widgets ที่ไม่ใช่ ttk
        for widget in self.root.winfo_children():
            self.update_widget_colors(widget)

    def update_widget_colors(self, widget):
        """อัปเดตสีของ widget รวมถึง children"""
        try:
            # อัปเดตสีตามประเภทของ widget
            if isinstance(widget, tk.Frame) and not isinstance(widget, ttk.Frame):
                if (
                    widget.winfo_name() != "!frame"
                    or "header" not in widget.winfo_name()
                ):
                    widget.configure(bg=self.bg_color)
            elif isinstance(widget, tk.Label) and not isinstance(widget, ttk.Label):
                if (
                    "icon" not in widget.winfo_name()
                    and "logo" not in widget.winfo_name()
                ):
                    widget.configure(bg=self.bg_color, fg=self.text_color)
            elif isinstance(widget, tk.Canvas):
                if (
                    "gauge" not in widget.winfo_name()
                    and "preview" not in widget.winfo_name()
                ):
                    widget.configure(bg=self.bg_color)
            elif isinstance(widget, tk.Text):
                widget.configure(
                    bg=self.bg_color,
                    fg=self.text_color,
                    insertbackground=self.text_color,
                )

            # อัปเดต children widgets
            for child in widget.winfo_children():
                self.update_widget_colors(child)
        except Exception:
            # บาง widgets อาจไม่สามารถปรับแต่งได้
            pass

    def set_theme(self, theme_name):
        """ตั้งค่าและใช้งานธีม"""
        if theme_name != self.current_theme and theme_name in self.themes:
            self.current_theme = theme_name
            self.apply_theme(theme_name)

            # อัปเดตการตั้งค่า
            self.ui.app.config["theme"] = theme_name

            # ส่งคืนค่า True ถ้าเปลี่ยนธีมสำเร็จ
            return True
        return False
