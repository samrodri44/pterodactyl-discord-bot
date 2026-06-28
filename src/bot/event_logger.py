import asyncio
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__)
handler = RotatingFileHandler(filename="logs/events.log", encoding="utf-8", mode="w", maxBytes=5_000_000, backupCount=3)
formatter = logging.Formatter(fmt="%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S", style="%")

class EventLogger:
    def __init__(self):
        handler.setFormatter(formatter)
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        logger.propagate = False

    async def run(self, queue):
        while(True):
            try:
                message = await queue.get()
                logger.info(f"event_type={message.event_type} status={message.status} id={message.event_id} player_count={message.player_count}")
            except Exception:
                print(f"Logger error: {e}")
                await asyncio.sleep(5)
