import time

class Limits:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.reset_if_needed()

    def reset_if_needed(self):
        now = int(time.time())
        day = now // 86400
        hour = now // 3600
        if getattr(self, "_day", None) != day:
            self._day = day
            self.day_counts = {"likes": 0, "follows": 0, "comments": 0, "views": 0}
        if getattr(self, "_hour", None) != hour:
            self._hour = hour
            self.hour_counts = {"likes": 0, "follows": 0, "comments": 0, "views": 0}

    def can(self, action: str) -> bool:
        self.reset_if_needed()
        pd = self.cfg["limits"]["per_day"][action]
        ph = self.cfg["limits"]["per_hour"][action]
        return self.day_counts[action] < pd and self.hour_counts[action] < ph

    def inc(self, action: str):
        self.reset_if_needed()
        self.day_counts[action] += 1
        self.hour_counts[action] += 1
