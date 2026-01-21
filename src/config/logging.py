import sys
from typing import Any, Mapping

from loguru import logger

from .config import settings


def format_record(record: Mapping[str, Any]) -> str:
    fmt = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level:<8}</level> | <level>{message}</level>"
    if record["extra"]:
        fmt += " | <magenta>{extra}</magenta>"
    return fmt + "\n"


def init_logger() -> None:
    logger.remove()
    logger.add(
        sys.stdout,
        format=format_record,
        level=settings.logger.log_level,
        backtrace=True,
        diagnose=True,
        enqueue=True,
    )
