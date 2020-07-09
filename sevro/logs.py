import logging

import colored


def setup_logging():
    """Configure the default logger to include the time."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s: %(msg)s")


def log(msg: str):
    """Log using the default logger at info level."""
    logging.info(msg)


def logc(color: str, msg: str):
    """Print a colorized message, resetting the terminal colors at the end."""
    log(color + msg + colored.style.RESET)
