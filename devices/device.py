import logging
import random
from devices.adb import ADB
from devices.screen import screencap_bgr

class ADBDevice:
    def __init__(self, device_id: str, cfg: dict):
        self.device_id = device_id
        self.cfg = cfg
        self.adb = ADB(device_id=device_id)

        self.log = logging.getLogger(f"device:{device_id}")
        self.log.setLevel(logging.INFO)
        fh = logging.FileHandler(f"logs/device_{device_id.replace(':','_')}.log", encoding="utf-8")
        fmt = logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")
        fh.setFormatter(fmt)
        if not self.log.handlers:
            self.log.addHandler(fh)

    def get_state(self) -> str:
        return self.adb.check_output(["get-state"]).strip()

    def screenshot(self):
        mode = self.cfg["adb"].get("screencap_mode", "exec-out")
        return screencap_bgr(self.adb, mode=mode)

    def tap(self, x: int, y: int, jitter: int = 8):
        jx = x + random.randint(-jitter, jitter)
        jy = y + random.randint(-jitter, jitter)
        self.adb.shell_call(f"input tap {jx} {jy}")

    def swipe(self, x1: int, y1: int, x2: int, y2: int, dur_ms: int = 300):
        self.adb.shell_call(f"input swipe {x1} {y1} {x2} {y2} {dur_ms}")

    def back(self):
        self.adb.shell_call("input keyevent 4")

    def home(self):
        self.adb.shell_call("input keyevent 3")

    def force_stop(self, package: str):
        self.adb.shell_call(f"am force-stop {package}")

    def launch(self, package: str):
        # monkey — самый простой запуск
        self.adb.shell_call(f"monkey -p {package} 1")

    def resumed_activity(self) -> str:
        # универсальнее чем window focus на разных прошивках
        out = self.adb.shell("dumpsys activity activities", timeout=30)
        # ищем строку ResumedActivity / mResumedActivity
        for line in out.splitlines():
            if "ResumedActivity" in line or "mResumedActivity" in line or "topResumedActivity" in line:
                return line.strip()
        return ""
