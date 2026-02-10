from dataclasses import dataclass


@dataclass
class Snapshot:
    player_count: int = 0
    ws_connected: bool = False
    last_update: str = "never"
    status: str = "offline"
    uptime: float = 0
