import os
import time
import yaml
import multiprocessing as mp
import logging
import signal
import sys

from devices.device import ADBDevice
from accounts.store import AccountStore
from logic.state_machine import AccountStateMachine
from devices.discovery import discover_devices

logger = logging.getLogger(__name__)

SHUTDOWN = False

def validate_config(cfg: dict):
    if not isinstance(cfg, dict):
        raise RuntimeError("Config must be a mapping (config.yaml)")
    # basic checks
    if "farm" not in cfg or "tick_seconds" not in cfg.get("farm", {}):
        raise RuntimeError("Config must contain farm.tick_seconds")
    if "vision" not in cfg or "match_threshold" not in cfg.get("vision", {}):
        raise RuntimeError("Config must contain vision.match_threshold")
    if "limits" not in cfg or "per_day" not in cfg.get("limits", {}) or "per_hour" not in cfg.get("limits", {}):
        raise RuntimeError("Config must contain limits.per_day and limits.per_hour")

def handle_signal(signum, frame):
    global SHUTDOWN
    logger.info("Received signal %s, shutting down", signum)
    SHUTDOWN = True

def run_worker(device_id: str, cfg: dict):
    os.makedirs("logs", exist_ok=True)
    device = ADBDevice(device_id=device_id, cfg=cfg)

    store = AccountStore("data/accounts")
    # В MVP: 1 аккаунт на 1 девайс (ты потом расширишь маппинг)
    account = store.pick_account_for_device(device_id)
    sm = AccountStateMachine(cfg=cfg, device=device, account=account, store=store)

    device.log.info(f"Worker started. device={device_id} account={account.account_id}")

    while True:
        if SHUTDOWN:
            device.log.info("Worker shutting down: device=%s", device_id)
            return
        try:
            sm.tick()
        except Exception as e:
            device.log.exception(f"Tick error: {e}")
            # небольшой backoff
            time.sleep(3)

        # protect against misconfigured cfg
        tick_seconds = cfg.get("farm", {}).get("tick_seconds", 5)
        time.sleep(tick_seconds)

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')

    with open("config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    # validate
    validate_config(cfg)

    # setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    if cfg.get("adb", {}).get("autodiscover", False):
        device_ids = discover_devices(cfg["adb"].get("include_prefix"))
    else:
        device_ids = cfg.get("adb", {}).get("device_ids", [])
    procs = []

    for d in device_ids:
        p = mp.Process(target=run_worker, args=(d, cfg), daemon=False)
        p.start()
        procs.append(p)

    # wait for shutdown
    try:
        while not SHUTDOWN:
            time.sleep(0.5)
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received, shutting down")

    # terminate children
    for p in procs:
        if p.is_alive():
            p.terminate()
            p.join(timeout=5)

    logger.info("Main exited")

if __name__ == "__main__":
    main()
