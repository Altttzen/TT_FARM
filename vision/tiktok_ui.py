import os
from typing import Optional, Dict
import numpy as np
import logging

from vision.match import load_template, match_template
from vision.roi import right_column_roi

logger = logging.getLogger(__name__)
TPL_DIR = os.path.join("vision", "templates")

class TikTokUI:
    def __init__(self, cfg: dict):
        self.cfg = cfg

        # Validate required vision config
        try:
            th_val = cfg["vision"]["match_threshold"]
            x_start_val = cfg["vision"]["roi_right_col_x_start_ratio"]
        except Exception as e:
            raise RuntimeError("Missing required vision configuration: 'vision.match_threshold' or 'vision.roi_right_col_x_start_ratio'") from e

        try:
            self.th = float(th_val)
        except Exception:
            raise RuntimeError("vision.match_threshold must be a number between 0.0 and 1.0")
        if not (0.0 <= self.th <= 1.0):
            raise RuntimeError("vision.match_threshold must be between 0.0 and 1.0")

        try:
            self.x_start = float(x_start_val)
        except Exception:
            raise RuntimeError("vision.roi_right_col_x_start_ratio must be a number between 0.0 and 1.0")
        if not (0.0 <= self.x_start <= 1.0):
            logger.warning("roi_right_col_x_start_ratio out of range, clamping to [0.0,1.0]: %s", self.x_start)
            self.x_start = min(max(self.x_start, 0.0), 1.0)

        # Load templates. like_unliked.png is required; others are optional.
        like_unliked_path = os.path.join(TPL_DIR, "like_unliked.png")
        if not os.path.exists(like_unliked_path):
            raise RuntimeError(f"Required template not found: {like_unliked_path}. Please add required templates to vision/templates")
        self.tpl_like_unliked = load_template(like_unliked_path)

        self.tpl_like_liked = None
        liked_path = os.path.join(TPL_DIR, "like_liked.png")
        if os.path.exists(liked_path):
            try:
                self.tpl_like_liked = load_template(liked_path)
            except FileNotFoundError:
                logger.exception("Failed to load like_liked.png despite exists check")

        self.tpl_follow_plus = None
        fp = os.path.join(TPL_DIR, "follow_plus.png")
        if os.path.exists(fp):
            try:
                self.tpl_follow_plus = load_template(fp)
            except FileNotFoundError:
                logger.exception("Failed to load follow_plus.png despite exists check")

        self.tpl_comment_btn = None
        cb = os.path.join(TPL_DIR, "comment_btn.png")
        if os.path.exists(cb):
            try:
                self.tpl_comment_btn = load_template(cb)
            except FileNotFoundError:
                logger.exception("Failed to load comment_btn.png despite exists check")

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