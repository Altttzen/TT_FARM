import random
from actions.humanize import sleep_jitter

def swipe_up(device, img_shape, speed="normal"):
    h, w = img_shape[:2]
    x = int(w * random.uniform(0.45, 0.55))
    y1 = int(h * random.uniform(0.75, 0.85))
    y2 = int(h * random.uniform(0.20, 0.30))

    dur = {"slow": 520, "normal": 320, "fast": 220}[speed]
    device.swipe(x, y1, x, y2, dur_ms=dur)
    sleep_jitter(0.6, 0.25)
