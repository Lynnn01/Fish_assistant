from utils.constants import UI_CONSTANTS, PIXEL_COLORS


# แก้ไข styles.py เพิ่ม style สำหรับ label ที่มีสีพิเศษ
def apply_styles(style):
    """
    กำหนดสไตล์ของ UI ทั้งหมด

    Args:
        style: ttk.Style object สำหรับการกำหนดสไตล์
    """
    # ใช้ theme เริ่มต้น
    style.theme_use("default")

    # สีที่ใช้
    primary_color = PIXEL_COLORS["PRIMARY_BLUE"]
    secondary_color = PIXEL_COLORS["SECONDARY_SALMON"]
    success_color = PIXEL_COLORS["SUCCESS_GREEN"]
    danger_color = PIXEL_COLORS["DANGER_RED"]
    warning_color = PIXEL_COLORS["WARNING_YELLOW"]
    bg_color = PIXEL_COLORS["BACKGROUND_DARK"]
    text_color = PIXEL_COLORS["TEXT_LIGHT"]
    panel_bg = PIXEL_COLORS["PANEL_BG"]
    accent_color = PIXEL_COLORS["ACCENT_BLUE"]

    # ฟอนต์
    font_family = UI_CONSTANTS["FONT_FAMILY"]

    # กำหนดสไตล์ปุ่มแบบพิกเซล
    style.configure(
        "Pixel.TButton",
        font=(font_family, 10, "bold"),
        background=primary_color,
        foreground=text_color,
        borderwidth=2,
        relief="raised",
    )

    style.configure(
        "PixelSuccess.TButton",
        font=(font_family, 10, "bold"),
        background=success_color,
        foreground=text_color,
        borderwidth=2,
        relief="raised",
    )

    style.configure(
        "PixelDanger.TButton",
        font=(font_family, 10, "bold"),
        background=danger_color,
        foreground=text_color,
        borderwidth=2,
        relief="raised",
    )

    # กำหนดสไตล์เฟรมและป้าย
    style.configure("Pixel.TFrame", background=bg_color)

    style.configure(
        "PixelPanel.TFrame",
        background=panel_bg,
        borderwidth=2,
        relief="raised",
    )

    style.configure(
        "Pixel.TLabel",
        background=bg_color,
        foreground=text_color,
        font=(font_family, 10),
    )

    style.configure(
        "PixelTitle.TLabel",
        background=bg_color,
        foreground=accent_color,
        font=(font_family, 12, "bold"),
    )

    # เพิ่ม style สำหรับ label ที่มีสีพิเศษ
    style.configure(
        "PixelSuccess.TLabel",
        background=bg_color,
        foreground=success_color,
        font=(font_family, 10, "bold"),
    )

    style.configure(
        "PixelDanger.TLabel",
        background=bg_color,
        foreground=danger_color,
        font=(font_family, 10, "bold"),
    )

    style.configure(
        "PixelWarning.TLabel",
        background=bg_color,
        foreground=warning_color,
        font=(font_family, 10, "bold"),
    )

    style.configure(
        "Pixel.TLabelframe",
        background=panel_bg,
        foreground=accent_color,
        borderwidth=2,
        relief="raised",
    )

    style.configure(
        "Pixel.TLabelframe.Label",
        background=panel_bg,
        foreground=accent_color,
        font=(font_family, 10, "bold"),
    )

    # กำหนดสไตล์เพิ่มเติมสำหรับ hover และ active states
    style.map(
        "Pixel.TButton",
        background=[("active", primary_color), ("disabled", bg_color)],
        foreground=[("disabled", panel_bg)],
    )

    style.map(
        "PixelSuccess.TButton",
        background=[("active", success_color), ("disabled", bg_color)],
        foreground=[("disabled", panel_bg)],
    )

    style.map(
        "PixelDanger.TButton",
        background=[("active", danger_color), ("disabled", bg_color)],
        foreground=[("disabled", panel_bg)],
    )
