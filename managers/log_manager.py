import logging


class LogManager:
    @staticmethod
    def setup():
        logging.basicConfig(
            format="%(asctime)s - %(levelname)s: %(message)s",
            datefmt='%Y-%m-%d:%H:%M:%S'
        )
        logging.getLogger().setLevel(logging.INFO)
