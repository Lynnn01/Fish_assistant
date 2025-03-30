import os
import json
import time
from datetime import datetime


class AnalyticsTracker:
    def __init__(self, stats_file="stats.json"):
        self.stats_file = stats_file
        self.stats = self.load_statistics()

        # สถิติสำหรับเซสชันปัจจุบัน
        self.current_session = {
            "start_time": time.time(),
            "catches": 0,
            "duration": 0,
            "clicks": 0,
        }

    def load_statistics(self):
        """โหลดสถิติจากไฟล์"""
        default_stats = {
            "total_catches": 0,
            "total_sessions": 0,
            "total_time": 0,
            "total_clicks": 0,
            "best_session": {"catches": 0, "date": "", "duration": 0},
            "history": [],
        }

        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, "r") as f:
                    return json.load(f)
            return default_stats
        except Exception:
            return default_stats

    def save_statistics(self):
        """บันทึกสถิติลงไฟล์"""
        try:
            with open(self.stats_file, "w") as f:
                json.dump(self.stats, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving statistics: {e}")
            return False

    def add_catch(self):
        """เพิ่มจำนวนปลาที่จับได้"""
        self.current_session["catches"] += 1
        self.stats["total_catches"] += 1

    def add_click(self):
        """เพิ่มจำนวนคลิก"""
        self.current_session["clicks"] += 1
        self.stats["total_clicks"] += 1

    def add_session_start(self):
        """บันทึกการเริ่มเซสชัน"""
        self.current_session = {
            "start_time": time.time(),
            "catches": 0,
            "duration": 0,
            "clicks": 0,
        }

    def add_session_end(self):
        """บันทึกการจบเซสชัน"""
        # คำนวณระยะเวลาเซสชัน
        duration = time.time() - self.current_session["start_time"]
        self.current_session["duration"] = duration
        self.stats["total_time"] += duration

        # เพิ่มจำนวนเซสชัน
        self.stats["total_sessions"] += 1

        # ตรวจสอบว่าเป็นเซสชันที่ดีที่สุดหรือไม่
        if self.current_session["catches"] > self.stats["best_session"]["catches"]:
            self.stats["best_session"] = {
                "catches": self.current_session["catches"],
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "duration": duration,
            }

        # เพิ่มประวัติ
        self.stats["history"].append(
            {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "catches": self.current_session["catches"],
                "duration": duration,
                "clicks": self.current_session["clicks"],
            }
        )

        # จำกัดประวัติไม่เกิน 100 รายการ
        if len(self.stats["history"]) > 100:
            self.stats["history"] = self.stats["history"][-100:]

        # บันทึกลงไฟล์
        self.save_statistics()

    def get_current_session_stats(self):
        """ดึงสถิติของเซสชันปัจจุบัน"""
        stats = self.current_session.copy()
        stats["duration"] = time.time() - stats["start_time"]

        # คำนวณอัตราจับปลาต่อชั่วโมง
        if stats["duration"] > 0:
            stats["catch_rate"] = (stats["catches"] / stats["duration"]) * 3600
        else:
            stats["catch_rate"] = 0

        return stats

    def get_all_time_stats(self):
        """ดึงสถิติทั้งหมด"""
        return self.stats
