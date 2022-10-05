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

    # quieten boto3 and related components
    logging.getLogger("boto3").setLevel(logging.CRITICAL)
    logging.getLogger("botocore").setLevel(logging.CRITICAL)
    logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)


def log(msg: str, level=logging.INFO):
    """Writes a message to the log"""
    LOGGER.log(level, msg)
