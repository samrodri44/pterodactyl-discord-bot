import logging

logger = logging.getLogger(__name__)
handler = logging.handlers.RotatingFileHandler(filename="discord.log", encoding="utf-8", mode="w", maxBytes=5_000_000, backupCount=3)
formatter = logging.Formatter(fmt="%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S", style="%")

class EventLogger:
    def __init__(self):
        logging.basicConfig(filename="events.log", level=logging.INFO)
        logger.info("Starting logger")

    def run(self, queue):
        try:
            while(True):
        except Exception:
            print("logger error: {e}")

