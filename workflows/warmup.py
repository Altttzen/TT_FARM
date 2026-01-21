import random
from actions.humanize import chance, sleep_jitter
from actions.gestures import swipe_up
from vision.tiktok_ui import TikTokUI

class WarmupWorkflow:
    def __init__(self, cfg: dict, device, limits):
        self.cfg = cfg
        self.device = device
        self.limits = limits
        self.ui = TikTokUI(cfg)

    def tick(self):
        img = self.device.screenshot()

        # 1) Просмотр (по сути “подождать”)
        view_min = self.cfg["warmup"]["view_seconds_min"]
        view_max = self.cfg["warmup"]["view_seconds_max"]
        sleep_jitter(random.uniform(view_min, view_max), 0.8)
        if self.limits.can("views"):
            self.limits.inc("views")

        # 2) Лайк (по вероятности и лимитам)
        if chance(self.cfg["warmup"]["like_chance"]) and self.limits.can("likes"):
            like = self.ui.find_like(img)
            if like and like["state"] == "unliked":
                self.device.tap(like["x"], like["y"])
                self.device.log.info(f"WARMUP like tap at {like['x']},{like['y']} score={like['score']:.2f}")
                self.limits.inc("likes")
                sleep_jitter(0.7, 0.3)

        # 3) Подписка (если у тебя есть follow_plus.png)
        if chance(self.cfg["warmup"]["follow_chance"]) and self.limits.can("follows"):
            f = self.ui.find_follow_plus(img)
            if f:
                self.device.tap(f["x"], f["y"])
                self.device.log.info(f"WARMUP follow tap at {f['x']},{f['y']} score={f['score']:.2f}")
                self.limits.inc("follows")
                sleep_jitter(0.9, 0.4)

        # 4) Коммент (каркас: нажать кнопку комментов; ввод текста — добавишь детект поля)
        if chance(self.cfg["warmup"]["comment_chance"]) and self.limits.can("comments"):
            c = self.ui.find_comment_btn(img)
            if c:
                self.device.tap(c["x"], c["y"])
                self.device.log.info(f"WARMUP comment btn tap at {c['x']},{c['y']} score={c['score']:.2f}")
                # в MVP считаем “попытку” коммента как действие
                self.limits.inc("comments")
                sleep_jitter(1.2, 0.6)
                self.device.back()
                sleep_jitter(0.6, 0.3)

        # 5) Свайп к следующему видео
        if chance(self.cfg["warmup"]["swipe_chance"]):
            swipe_up(self.device, img.shape, speed=random.choice(["slow", "normal", "fast"]))
