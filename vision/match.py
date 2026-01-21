import cv2
import numpy as np
from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass
class Match:
    center: Tuple[int, int]
    score: float
    rect: Tuple[int, int, int, int]  # x,y,w,h

def load_template(path: str) -> np.ndarray:
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"Template not found: {path}")
    return img

def match_template(hay_bgr: np.ndarray, tpl_bgr: np.ndarray, threshold: float) -> Optional[Match]:
    hay = cv2.cvtColor(hay_bgr, cv2.COLOR_BGR2GRAY)
    tpl = cv2.cvtColor(tpl_bgr, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(hay, tpl, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)

    if max_val < threshold:
        return None

    h, w = tpl.shape[:2]
    cx = int(max_loc[0] + w / 2)
    cy = int(max_loc[1] + h / 2)
    return Match(center=(cx, cy), score=float(max_val), rect=(max_loc[0], max_loc[1], w, h))
