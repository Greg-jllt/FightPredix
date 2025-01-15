import logging


def configure_logger(name: str) -> logging.Logger:

    logger = logging.getLogger(name)

    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    file_handler = logging.FileHandler(f"FightPredix_scraping\\logs\\{name}.log")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logging.captureWarnings(True)
    return logger
