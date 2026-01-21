import cv2
import numpy as np
from dataclasses import dataclass
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

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
    """Match template with safety checks.

    Returns None when matching is impossible (e.g. template larger than image or invalid inputs).
    """
    if hay_bgr is None or tpl_bgr is None:
        logger.debug("match_template: received None for haystack or template")
        return None

    # Ensure inputs are numpy arrays
    try:
        hay_shape = hay_bgr.shape
        tpl_shape = tpl_bgr.shape
    except Exception:
        logger.debug("match_template: invalid image objects passed")
        return None

    # Template must not be larger than haystack
    if tpl_shape[0] > hay_shape[0] or tpl_shape[1] > hay_shape[1]:
        logger.debug("match_template: template %s is larger than haystack %s, skipping",
                     tpl_shape, hay_shape)
        return None

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
