import os
import time
import yaml
import multiprocessing as mp

from devices.device import ADBDevice
from accounts.store import AccountStore
from logic.state_machine import AccountStateMachine
from devices.discovery import discover_devices

def run_worker(device_id: str, cfg: dict):
    os.makedirs("logs", exist_ok=True)
    device = ADBDevice(device_id=device_id, cfg=cfg)

    store = AccountStore("data/accounts")
    # В MVP: 1 аккаунт на 1 девайс (ты потом расширишь маппинг)
    account = store.pick_account_for_device(device_id)
    sm = AccountStateMachine(cfg=cfg, device=device, account=account, store=store)

    device.log.info(f"Worker started. device={device_id} account={account.account_id}")

    while True:
        try:
            sm.tick()
        except Exception as e:
            device.log.exception(f"Tick error: {e}")
            # небольшой backoff
            time.sleep(3)

        time.sleep(cfg["farm"]["tick_seconds"])

def main():
    with open("config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    if cfg["adb"].get("autodiscover", False):
        device_ids = discover_devices(cfg["adb"].get("include_prefix"))
    else:
        device_ids = cfg["adb"]["device_ids"]
    procs = []

    for d in device_ids:
        p = mp.Process(target=run_worker, args=(d, cfg), daemon=False)
        p.start()
        procs.append(p)

    for p in procs:
        p.join()

if __name__ == "__main__":
    main()
