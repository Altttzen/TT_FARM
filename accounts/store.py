import json
import os
from accounts.model import Account

class AccountStore:
    def __init__(self, dir_path: str):
        self.dir_path = dir_path

    def _load_all(self):
        accs = []
        for fn in os.listdir(self.dir_path):
            if not fn.endswith(".json"):
                continue
            path = os.path.join(self.dir_path, fn)
            with open(path, "r", encoding="utf-8") as f:
                d = json.load(f)
            accs.append(Account(**d))
        return accs

    def pick_account_for_device(self, device_id: str) -> Account:
        accs = self._load_all()
        # простая стратегия: device_hint совпал — берём его; иначе первый
        for a in accs:
            if a.device_hint and a.device_hint == device_id:
                return a
        if not accs:
            raise RuntimeError("No accounts found in data/accounts")
        return accs[0]
