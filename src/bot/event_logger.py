import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__)
handler = RotatingFileHandler(filename="events.log", encoding="utf-8", mode="w", maxBytes=5_000_000, backupCount=3)
formatter = logging.Formatter(fmt="%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S", style="%")

class EventLogger:
    def __init__(self):
        logger.setLevel(logging.INFO)
        logger.info("Starting logger")
        logger.info("Attaching formatter to handler")
        handler.setFormatter(formatter)
        logger.info("Adding handler...")
        logger.addHandler(handler)

    async def run(self, queue):
        try:
            while(True):
                message = await queue.get()
                logger.info(f"event_type={message.event_type} status={message.status} id={message.event_id} player_count={message.player_count}")
        except Exception:
            print("logger error: {e}")

if __name__ == "__main__":
    el = EventLogger()
    el.run(1)
