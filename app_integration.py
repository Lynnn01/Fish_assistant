import tkinter as tk
from ui.settings_ui import SettingsUI
from ui.main_menu import MainMenu
from utils.config_manager import ConfigManager


def integrate_settings(app, root):
    """
    เชื่อมโยงหน้าตั้งค่ากับแอพหลัก

    Args:
        app: แอพพลิเคชันหลัก
        root: หน้าต่างหลัก

    Returns:
        tuple: (config_manager, settings_ui, main_menu)
    """
    # สร้างตัวจัดการการตั้งค่า
    config_manager = ConfigManager("config.json")

    # ลงทะเบียนฟังก์ชันที่จะเรียกเมื่อการตั้งค่าเปลี่ยนแปลง
    config_manager.register_observer(lambda config: on_config_changed(app, config))

    # สร้างหน้าตั้งค่า
    settings_ui = SettingsUI(root, "config.json")

    # สร้างเมนูหลัก
    main_menu = MainMenu(root, settings_ui, config_manager, app)

    # เพิ่มคีย์ลัด
    setup_hotkeys(root, settings_ui)

    # ตั้งค่าการตรวจสอบการเปลี่ยนแปลงการตั้งค่าตามระยะเวลา
    schedule_config_check(root, config_manager)

    return config_manager, settings_ui, main_menu


def on_config_changed(app, config):
    """
    จัดการเมื่อการตั้งค่าเปลี่ยนแปลง

    Args:
        app: แอพพลิเคชันหลัก
        config: การตั้งค่าใหม่
    """
    print("การตั้งค่าเปลี่ยนแปลง:", config)

    # อัปเดตค่าเกณฑ์ต่างๆ
    if hasattr(app, "detector"):
        app.detector.line_threshold = config.get("line_threshold", 200)
        app.detector.color_threshold = config.get("color_threshold", 30)

    # อัปเดตค่าคูลดาวน์
    if hasattr(app, "action_cooldown"):
        app.action_cooldown = config.get("action_cooldown", 0.1)

    # อัปเดตค่าเกี่ยวกับโซน
    if hasattr(app, "red_zone_threshold"):
        app.red_zone_threshold = config.get("red_zone_threshold", 0.2)

    if hasattr(app, "buffer_zone_size"):
        app.buffer_zone_size = config.get("buffer_zone_size", 0.13)

    # อัปเดต UI (หากมีการเปลี่ยนแปลงสี)
    update_ui_colors(app, config)


def update_ui_colors(app, config):
    """
    อัปเดตสีของ UI จากการตั้งค่า

    Args:
        app: แอพพลิเคชันหลัก
        config: การตั้งค่าใหม่
    """
    if hasattr(app, "ui") and hasattr(app.ui, "gauge"):
        ui_colors = config.get("ui_colors", {})

        # ถ้ามีสีครบตามที่ต้องการให้อัปเดต
        if all(key in ui_colors for key in ["primary", "success", "danger", "warning"]):
            # อัปเดตสีเกจ
            gauge_colors = {
                "success": ui_colors.get("success", "#2ecc71"),
                "danger": ui_colors.get("danger", "#e74c3c"),
                "warning": ui_colors.get("warning", "#f39c12"),
                "bg": app.ui.bg_color,
                "accent": app.ui.accent_color,
                "crt": app.ui.crt_color,
            }

            app.ui.gauge.set_gauge_color(
                success_color=gauge_colors["success"],
                danger_color=gauge_colors["danger"],
                warning_color=gauge_colors["warning"],
                accent_color=gauge_colors["accent"],
                crt_color=gauge_colors["crt"],
            )

            # อัปเดต progress bar หากมี
            if hasattr(app.ui, "progress_bar"):
                app.ui.progress_bar.success_color = gauge_colors["success"]
                app.ui.progress_bar.danger_color = gauge_colors["danger"]
                app.ui.progress_bar.warning_color = gauge_colors["warning"]


def setup_hotkeys(root, settings_ui):
    """
    ตั้งค่าคีย์ลัดต่างๆ

    Args:
        root: หน้าต่างหลัก
        settings_ui: อินสแตนซ์ของ SettingsUI
    """
    # Ctrl+S เพื่อเปิดการตั้งค่า
    root.bind("<Control-s>", lambda e: settings_ui.open_settings())


def schedule_config_check(root, config_manager, interval=5000):
    """
    ตั้งเวลาตรวจสอบการเปลี่ยนแปลงการตั้งค่าตามระยะเวลา

    Args:
        root: หน้าต่างหลัก
        config_manager: อินสแตนซ์ของ ConfigManager
        interval: ระยะเวลาในการตรวจสอบ (มิลลิวินาที)
    """

    def check_config():
        config_manager.check_for_changes()
        root.after(interval, check_config)

    # เริ่มตรวจสอบตามระยะเวลา
    root.after(interval, check_config)
