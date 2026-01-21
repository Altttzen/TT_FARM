#!/usr/bin/env python3
import os
import sys
import yaml
import shutil
import subprocess
from datetime import datetime

CONFIG_PATH = "config.yaml"
BACKUP_DIR = "config_backups"

def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def save_config(cfg, path):
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, sort_keys=False, allow_unicode=True)

def backup_config(path):
    os.makedirs(BACKUP_DIR, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    dst = os.path.join(BACKUP_DIR, f"config.yaml.{ts}.bak")
    shutil.copy2(path, dst)
    return dst

def prompt_int(prompt, default=None):
    while True:
        val = input(prompt).strip()
        if val == "" and default is not None:
            return default
        try:
            v = int(val)
            if v < 0:
                print("Please enter a non-negative integer.")
                continue
            return v
        except ValueError:
            print("Please enter a valid integer (or press Enter to keep current).")

def prompt_float(prompt, default=None):
    while True:
        val = input(prompt).strip()
        if val == "" and default is not None:
            return default
        try:
            v = float(val)
            if v < 0:
                print("Please enter a non-negative number.")
                continue
            return v
        except ValueError:
            print("Please enter a valid number (or press Enter to keep current).")

def edit_limits(cfg):
    if "limits" not in cfg or "per_day" not in cfg["limits"] or "per_hour" not in cfg["limits"]:
        print("Configuration does not contain limits.per_day / limits.per_hour. Cannot edit limits.")
        return cfg

    per_day = cfg["limits"]["per_day"]
    per_hour = cfg["limits"]["per_hour"]

    actions = sorted(set(list(per_day.keys()) + list(per_hour.keys())))
    if not actions:
        print("No actions found in limits configuration to edit.")
        return cfg

    print("Detected actions:")
    for a in actions:
        pd = per_day.get(a, 0)
        ph = per_hour.get(a, 0)
        print(f" - {a}: per_day={{pd}}, per_hour={{ph}}")

    print("\nEnter new values for actions. Press Enter to keep current value.")
    for a in actions:
        cur_pd = per_day.get(a, 0)
        cur_ph = per_hour.get(a, 0)
        new_pd = prompt_int(f"{{a}} per_day (current={{cur_pd}}): ", default=cur_pd)
        new_ph = prompt_int(f"{{a}} per_hour (current={{cur_ph}}): ", default=cur_ph)
        per_day[a] = new_pd
        per_hour[a] = new_ph

    # Allow adding/ensuring 'swipes' action exists
    if 'swipes' not in per_day:
        print("\nYou can configure scrolls (swipes) limits. They are stored under action name 'swipes'.")
        add_sw = input("Add 'swipes' to limits? [y/N]: ").strip().lower()
        if add_sw == 'y':
            pd = prompt_int("swipes per_day (default 100): ", default=per_day.get('swipes', 100))
            ph = prompt_int("swipes per_hour (default 20): ", default=per_hour.get('swipes', 20))
            per_day['swipes'] = pd
            per_hour['swipes'] = ph

    cfg["limits"]["per_day"] = per_day
    cfg["limits"]["per_hour"] = per_hour
    return cfg

def edit_run_settings(cfg):
    farm = cfg.get('farm', {})
    print('\nRun settings:')
    current_run = farm.get('run_seconds', None)
    if current_run is None:
        print(' - run_seconds: not set (runs indefinitely)')
    else:
        print(f' - run_seconds: {{current_run}} seconds')

    new_run = input('Enter run duration in minutes (press Enter to keep current / blank = indefinite): ').strip()
    if new_run == '' and current_run is not None:
        # keep current
        pass
    elif new_run == '':
        if 'run_seconds' in farm:
            farm.pop('run_seconds')
    else:
        try:
            minutes = float(new_run)
            if minutes <= 0:
                print('Non-positive value; treating as indefinite (removing run_seconds)')
                farm.pop('run_seconds', None)
            else:
                farm['run_seconds'] = int(minutes * 60)
        except Exception:
            print('Invalid value, keeping current.')

    cfg['farm'] = farm
    return cfg

def edit_misc(cfg):
    # allow editing farm.tick_seconds and vision thresholds as convenience
    print("\nOptional: Edit misc parameters (press Enter to keep current).")
    farm = cfg.get("farm", {})
    tick = farm.get("tick_seconds")
    try:
        tick_val = float(tick)
    except Exception:
        tick_val = None
    if tick_val is not None:
        new_tick = input(f"farm.tick_seconds (current={{tick_val}}): ").strip()
        if new_tick != "":
            try:
                farm["tick_seconds"] = float(new_tick)
            except Exception:
                print("Invalid value, keeping current.")
    cfg["farm"] = farm

    vision = cfg.get("vision", {})
    mt = vision.get("match_threshold")
    try:
        mt_val = float(mt)
    except Exception:
        mt_val = None
    if mt_val is not None:
        new_mt = input(f"vision.match_threshold (current={{mt_val}}): ").strip()
        if new_mt != "":
            try:
                vision["match_threshold"] = float(new_mt)
            except Exception:
                print("Invalid value, keeping current.")
    cfg["vision"] = vision
    return cfg

def main():
    if not os.path.exists(CONFIG_PATH):
        print(f"Config not found at {{CONFIG_PATH}}. Create a config.yaml first.")
        sys.exit(1)

    cfg = load_config(CONFIG_PATH)
    print("Interactive Control Panel — edit action limits and run settings")

    cfg = edit_limits(cfg)
    cfg = edit_run_settings(cfg)
    cfg = edit_misc(cfg)

    print("\nSaving configuration...")
    bak = backup_config(CONFIG_PATH)
    save_config(cfg, CONFIG_PATH)
    print(f"Saved. Backup created at: {{bak}}")

    run_now = input("Run main.py now with the updated config? [y/N]: ").strip().lower()
    if run_now == "y":
        print("Starting main.py... (press Ctrl-C to stop)")
        try:
            subprocess.run([sys.executable, "main.py"], check=False)
        except KeyboardInterrupt:
            print("Execution interrupted by user.")

if __name__ == '__main__':
    main()
