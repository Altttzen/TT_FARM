import subprocess
from typing import List, Optional

class ADB:
    def __init__(self, device_id: Optional[str] = None):
        self.device_id = device_id

    def _base(self) -> List[str]:
        cmd = ["adb"]
        if self.device_id:
            cmd += ["-s", self.device_id]
        return cmd

    def check_output(self, args: List[str], timeout: int = 30) -> str:
        out = subprocess.check_output(self._base() + args, timeout=timeout)
        return out.decode("utf-8", errors="ignore")

    def check_output_bytes(self, args: List[str], timeout: int = 30) -> bytes:
        return subprocess.check_output(self._base() + args, timeout=timeout)

    def check_call(self, args: List[str], timeout: int = 30) -> None:
        subprocess.check_call(self._base() + args, timeout=timeout)

    def shell(self, cmd: str, timeout: int = 30) -> str:
        return self.check_output(["shell", cmd], timeout=timeout)

    def shell_call(self, cmd: str, timeout: int = 30) -> None:
        self.check_call(["shell", cmd], timeout=timeout)
