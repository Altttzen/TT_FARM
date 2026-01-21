import subprocess

def discover_devices(include_prefix: str | None = None) -> list[str]:
    out = subprocess.check_output(["adb", "devices"], text=True, errors="ignore")
    ids = []
    for line in out.splitlines():
        line = line.strip()
        if not line or line.startswith("List of devices"):
            continue
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "device":
            dev = parts[0]
            if include_prefix and not dev.startswith(include_prefix):
                continue
            ids.append(dev)
    return ids
