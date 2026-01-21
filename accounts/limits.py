import time

class Limits:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        # Validate limits structure
        limits_cfg = cfg.get("limits") if isinstance(cfg, dict) else None
        if not limits_cfg or "per_day" not in limits_cfg or "per_hour" not in limits_cfg:
            raise RuntimeError("Configuration 'limits.per_day' and 'limits.per_hour' are required in config")

        self.per_day = limits_cfg["per_day"]
        self.per_hour = limits_cfg["per_hour"]
        # derive allowed actions from per_day keys
        self.allowed_actions = set(self.per_day.keys())

        self.reset_if_needed()

    def reset_if_needed(self):
        now = int(time.time())
        day = now // 86400
        hour = now // 3600
        if getattr(self, "_day", None) != day:
            self._day = day
            # initialize counts for allowed actions
            self.day_counts = {k: 0 for k in self.allowed_actions}
        if getattr(self, "_hour", None) != hour:
            self._hour = hour
            self.hour_counts = {k: 0 for k in self.allowed_actions}

    def can(self, action: str) -> bool:
        if action not in self.allowed_actions:
            return False
        self.reset_if_needed()
        pd = int(self.per_day.get(action, 0))
        ph = int(self.per_hour.get(action, 0))
        return self.day_counts.get(action, 0) < pd and self.hour_counts.get(action, 0) < ph

    def inc(self, action: str):
        if action not in self.allowed_actions:
            raise ValueError(f"Unknown action: {action}")
        self.reset_if_needed()
        self.day_counts[action] += 1
        self.hour_counts[action] += 1
