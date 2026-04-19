from dataclasses import dataclass


@dataclass
class Snapshot:
    player_count: int = 0
    ws_connected: bool = False
    last_update: str = "never"
    status: str = "offline"
    uptime: float = 0

@dataclass
class ServerEvent:
    event_type: str
    correlation_id: str | None
    status: str
    player_count: int
    timestamp: datetime
