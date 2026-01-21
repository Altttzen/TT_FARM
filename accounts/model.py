from dataclasses import dataclass, field
from typing import Dict

@dataclass
class Account:
    account_id: str
    device_hint: str = ""
    stats: Dict = field(default_factory=dict)
