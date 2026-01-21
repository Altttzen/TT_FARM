import time
from accounts.limits import Limits
from actions.humanize import chance, sleep_jitter
from workflows.warmup import WarmupWorkflow
from workflows.posting import PostingWorkflow

TIKTOK_PKG = "com.zhiliaoapp.musically"

class AccountStateMachine:
    def __init__(self, cfg: dict, device, account, store):
        self.cfg = cfg
        self.device = device
        self.account = account
        self.store = store
        self.limits = Limits(cfg)

        self.warmup = WarmupWorkflow(cfg, device, self.limits)
        self.posting = PostingWorkflow(cfg, device, self.limits)

        self._last_launch = 0

    def ensure_tiktok(self):
        # если давно не запускали — запускаем
        if time.time() - self._last_launch > 120:
            self.device.launch(TIKTOK_PKG)
            self._last_launch = time.time()
            sleep_jitter(3.0, 1.0)

    def tick(self):
        self.ensure_tiktok()

        # posting в MVP выключен по умолчанию (config.yaml posting.enabled)
        if self.cfg["posting"].get("enabled", False):
            self.posting.tick()

        # прогрев — постоянно, но с лимитами
        self.warmup.tick()
