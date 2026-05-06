from dataclasses import dataclass
from datetime import datetime
import uuid
from enum import StrEnum, auto


@dataclass
class Snapshot:
    player_count: int = 0
    ws_connected: bool = False
    last_update: str = "never"
    status: str = "offline"
    uptime: float = 0

@dataclass
class ServerEvent:
    event_type: EventType
    event_id : str = uuid.uuid4()
    status: str = "unknown"
    player_count: int = 0
    timestamp: datetime = datetime.now()

class EventType(StrEnum):
    SERVER_STARTED = "server_started"
    SERVER_STOPPED = "server_stopped"
