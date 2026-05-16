import logging

logger = logging.getLogger(__name__)

class EventLogger:
    def __init__(self):
        logging.basicConfig(filename="events.log", level=logging.INFO)
        logger.info("Starting logger")

    def run(self, queue):
        try:
            while(True):
        except Exception:
            print("logger error: {e}")

