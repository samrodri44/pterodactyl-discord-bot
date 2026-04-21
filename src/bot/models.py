from dataclasses import dataclass
from datetime import datetime
import uuid


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
    correlation_id: str = uuid.uuid4()
    status: str = "unknown"
    player_count: int = 0
    timestamp: datetime = datetime.now()
