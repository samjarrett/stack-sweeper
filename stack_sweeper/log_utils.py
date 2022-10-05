import logging

LOGGER = logging.getLogger()


def log_setup(level: str = "INFO"):  # pragma: no cover
    """Configure base logging"""
    log_level = getattr(logging, level.upper(), None)
    if not isinstance(log_level, int):
        raise ValueError(f"Invalid log level: {level}")

    logging.basicConfig(
        level=log_level, format="%(asctime)s %(levelname)-2s: %(message)s"
    )


def log(msg: str, level=logging.INFO):
    """Writes a message to the log"""
    LOGGER.log(level, msg)
