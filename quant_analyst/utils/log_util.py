from loguru import logger


def get_logger():
    logger.add("file.log", level="DEBUG")
    return logger