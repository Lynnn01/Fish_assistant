from utils.constants import UI_CONSTANTS, PIXEL_COLORS


def apply_settings_styles(style):
    """
    เพิ่มสไตล์เฉพาะสำหรับหน้าตั้งค่า

    Args:
        style: ttk.Style object สำหรับการกำหนดสไตล์
    """
    # สีที่ใช้
    bg_color = PIXEL_COLORS["BACKGROUND_DARK"]
    text_color = PIXEL_COLORS["TEXT_LIGHT"]
    panel_bg = PIXEL_COLORS["PANEL_BG"]
    primary_color = PIXEL_COLORS["PRIMARY_BLUE"]
    accent_color = PIXEL_COLORS["ACCENT_BLUE"]

    # ฟอนต์
    font_family = UI_CONSTANTS["FONT_FAMILY"]

    # กำหนดสไตล์สำหรับ Entry
    style.configure(
        "Pixel.TEntry",
        fieldbackground=panel_bg,
        foreground=text_color,
        insertcolor=text_color,
        font=(font_family, 10),
        borderwidth=1,
    )

    # กำหนดสไตล์สำหรับสไลเดอร์
    style.configure(
        "Pixel.Horizontal.TScale",
        background=bg_color,
        troughcolor=panel_bg,
        sliderrelief="flat",
        sliderthickness=15,
        sliderlength=20,
        borderwidth=1,
    )

    # กำหนดสไตล์สำหรับ Notebook
    style.configure("TNotebook", background=bg_color, tabmargins=[2, 5, 2, 0])

    style.configure(
        "TNotebook.Tab",
        background=panel_bg,
        foreground=text_color,
        padding=[10, 2],
        font=(font_family, 10),
    )

    style.map(
        "TNotebook.Tab",
        background=[("selected", primary_color), ("active", accent_color)],
        foreground=[("selected", text_color), ("active", text_color)],
    )

    # กำหนดสไตล์สำหรับ Separator
    style.configure("TSeparator", background=accent_color)

    # กำหนดสไตล์สำหรับ Checkbutton
    style.configure(
        "Pixel.TCheckbutton",
        background=bg_color,
        foreground=text_color,
        font=(font_family, 10),
    )

    style.map(
        "Pixel.TCheckbutton",
        background=[("active", bg_color)],
        foreground=[("active", accent_color)],
    )

    # กำหนดสไตล์สำหรับ Radiobutton
    style.configure(
        "Pixel.TRadiobutton",
        background=bg_color,
        foreground=text_color,
        font=(font_family, 10),
    )

    style.map(
        "Pixel.TRadiobutton",
        background=[("active", bg_color)],
        foreground=[("active", accent_color)],
    )
