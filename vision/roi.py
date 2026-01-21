import numpy as np
import logging

logger = logging.getLogger(__name__)

def right_column_roi(img: np.ndarray, x_start_ratio: float = 0.62):
    h, w = img.shape[:2]
    # Validate ratio
    try:
        xr = float(x_start_ratio)
    except Exception:
        xr = 0.62
    if xr < 0.0 or xr > 1.0:
        logger.warning("right_column_roi: x_start_ratio out of bounds: %s, clamping", xr)
        xr = min(max(xr, 0.0), 1.0)

    x0 = int(w * xr)
    if x0 >= w:
        x0 = max(0, w - 1)
    roi = img[:, x0:w]
    # If ROI is empty, fallback to whole image
    if roi.size == 0:
        logger.warning("right_column_roi: computed empty ROI, falling back to full image")
        return img, 0, 0
    return roi, x0, 0

def feed_area_roi(img: np.ndarray):
    h, w = img.shape[:2]
    # примерная область видео, чтобы не ловить UI сверху/снизу
    y0 = int(h * 0.12)
    y1 = int(h * 0.88)
    if y0 >= y1:
        y0 = 0
        y1 = h
    return img[y0:y1, :], 0, y0
