import tkinter as tk
from tkinter import ttk


class TabPanel:
    def __init__(self, parent, theme_manager):
        self.parent = parent
        self.theme_manager = theme_manager

        # สร้างแท็บหลัก
        self.tab_buttons = []
        self.tabs = []
        self.current_tab = 0

        # สร้างเฟรมสำหรับแท็บ
        self.tab_header = ttk.Frame(parent)
        self.tab_header.pack(fill="x", pady=5)

        # สร้างเฟรมสำหรับเนื้อหา
        self.content_frame = ttk.Frame(parent)
        self.content_frame.pack(fill="both", expand=True)

    def add_tab(self, title, icon=""):
        """เพิ่มแท็บใหม่และสร้างปุ่มสำหรับแท็บ"""
        # สร้างปุ่มสำหรับแท็บ
        button_text = f"{icon} {title}" if icon else title
        button = ttk.Button(
            self.tab_header,
            text=button_text,
            command=lambda idx=len(self.tabs): self.switch_tab(idx),
        )
        self.tab_buttons.append(button)

        # สร้างเฟรมสำหรับเนื้อหาแท็บ
        tab_frame = ttk.Frame(self.content_frame)
        self.tabs.append(tab_frame)

        # จัดวางปุ่ม
        self.arrange_tab_buttons()

        # ถ้าเป็นแท็บแรก ให้แสดงทันที
        if len(self.tabs) == 1:
            self.switch_tab(0)

        return tab_frame

    def switch_tab(self, tab_index):
        """สลับไปยังแท็บที่ระบุ"""
        # ซ่อนแท็บปัจจุบัน
        if self.current_tab < len(self.tabs):
            self.tabs[self.current_tab].pack_forget()
            self.tab_buttons[self.current_tab].configure(style="TButton")

        # แสดงแท็บใหม่
        self.tabs[tab_index].pack(fill="both", expand=True)
        self.tab_buttons[tab_index].configure(style="Accent.TButton")

        # อัปเดตแท็บปัจจุบัน
        self.current_tab = tab_index

    def arrange_tab_buttons(self):
        """จัดวางปุ่มแท็บ"""
        # ลบปุ่มเดิมออกทั้งหมด
        for button in self.tab_buttons:
            button.pack_forget()

        # จัดวางปุ่มใหม่
        for button in self.tab_buttons:
            button.pack(side="left", padx=2, pady=2)

    def get_tab(self, tab_index):
        """ดึงเฟรมของแท็บตามดัชนี"""
        if 0 <= tab_index < len(self.tabs):
            return self.tabs[tab_index]
        return None

    def rebuild_tab(self, tab_index):
        """สร้างแท็บใหม่ (สำหรับการอัปเดตเนื้อหา)"""
        if 0 <= tab_index < len(self.tabs):
            # ลบเนื้อหาเดิม
            for widget in self.tabs[tab_index].winfo_children():
                widget.destroy()

            # ถ้าเป็นแท็บปัจจุบัน ให้โหลดใหม่
            if tab_index == self.current_tab:
                self.tabs[tab_index].pack_forget()
                self.tabs[tab_index].pack(fill="both", expand=True)

            return self.tabs[tab_index]
        return None
