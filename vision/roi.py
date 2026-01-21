import numpy as np

def right_column_roi(img: np.ndarray, x_start_ratio: float = 0.62):
    h, w = img.shape[:2]
    x0 = int(w * x_start_ratio)
    return img[:, x0:w], x0, 0

def feed_area_roi(img: np.ndarray):
    h, w = img.shape[:2]
    # примерная область видео, чтобы не ловить UI сверху/снизу
    y0 = int(h * 0.12)
    y1 = int(h * 0.88)
    return img[y0:y1, :], 0, y0
