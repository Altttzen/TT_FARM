import cv2
import numpy as np
from devices.adb import ADB

def screencap_bgr(adb: ADB, mode: str = "exec-out") -> np.ndarray:
    """
    mode:
      - exec-out: adb exec-out screencap -p (быстро)
      - file: через /sdcard (медленнее, но иногда стабильнее)
    """
    if mode == "exec-out":
        png = adb.check_output_bytes(["exec-out", "screencap", "-p"], timeout=30)
        img = cv2.imdecode(np.frombuffer(png, np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            raise RuntimeError("Failed to decode screencap")
        return img

    adb.shell_call("screencap -p /sdcard/__screen.png", timeout=30)
    png = adb.check_output_bytes(["exec-out", "cat", "/sdcard/__screen.png"], timeout=30)
    img = cv2.imdecode(np.frombuffer(png, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise RuntimeError("Failed to decode screencap(file)")
    return img
