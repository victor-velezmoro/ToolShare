import logging
from logging.handlers import RotatingFileHandler

def setup_logging(log_file: str = "app.log"):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            RotatingFileHandler(log_file, maxBytes=1000000, backupCount=3),
            logging.StreamHandler(),
        ],
    )

    logger = logging.getLogger(__name__)
    return logger

# Initialize logging
logger = setup_logging()
