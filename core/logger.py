import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("share_images")
logger.setLevel(logging.INFO)

handler = RotatingFileHandler("app.log", maxBytes=2000000, backupCount=10)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)

def get_logger():
    return logger
