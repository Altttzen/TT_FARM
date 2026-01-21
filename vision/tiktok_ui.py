import os
from typing import Optional, Dict
import numpy as np

from vision.match import load_template, match_template
from vision.roi import right_column_roi

TPL_DIR = os.path.join("vision", "templates")

class TikTokUI:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.th = float(cfg["vision"]["match_threshold"])
        self.x_start = float(cfg["vision"]["roi_right_col_x_start_ratio"])

        self.tpl_like_unliked = load_template(os.path.join(TPL_DIR, "like_unliked.png"))
        self.tpl_like_liked = None
        liked_path = os.path.join(TPL_DIR, "like_liked.png")
        if os.path.exists(liked_path):
            self.tpl_like_liked = load_template(liked_path)

        self.tpl_follow_plus = None
        fp = os.path.join(TPL_DIR, "follow_plus.png")
        if os.path.exists(fp):
            self.tpl_follow_plus = load_template(fp)

        self.tpl_comment_btn = None
        cb = os.path.join(TPL_DIR, "comment_btn.png")
        if os.path.exists(cb):
            self.tpl_comment_btn = load_template(cb)

    def find_like(self, img: np.ndarray) -> Optional[Dict]:
        roi, ox, oy = right_column_roi(img, self.x_start)

        hit = match_template(roi, self.tpl_like_unliked, self.th)
        if hit:
            return {"state": "unliked", "x": hit.center[0] + ox, "y": hit.center[1] + oy, "score": hit.score}

        if self.tpl_like_liked is not None:
            hit2 = match_template(roi, self.tpl_like_liked, self.th)
            if hit2:
                return {"state": "liked", "x": hit2.center[0] + ox, "y": hit2.center[1] + oy, "score": hit2.score}

        return None

    def find_follow_plus(self, img: np.ndarray) -> Optional[Dict]:
        if self.tpl_follow_plus is None:
            return None
        roi, ox, oy = right_column_roi(img, self.x_start)
        hit = match_template(roi, self.tpl_follow_plus, self.th)
        if not hit:
            return None
        return {"x": hit.center[0] + ox, "y": hit.center[1] + oy, "score": hit.score}

    def find_comment_btn(self, img: np.ndarray) -> Optional[Dict]:
        if self.tpl_comment_btn is None:
            return None
        roi, ox, oy = right_column_roi(img, self.x_start)
        hit = match_template(roi, self.tpl_comment_btn, self.th)
        if not hit:
            return None
        return {"x": hit.center[0] + ox, "y": hit.center[1] + oy, "score": hit.score}
