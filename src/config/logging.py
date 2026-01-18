import sys
from pathlib import Path
from typing import Any, Mapping

from loguru import logger

from .config import SRC_DIR, settings


def format_record(record: Mapping[str, Any]) -> str:
    record["extra"]["rel_path"] = Path(record["file"].path).relative_to(SRC_DIR)
    result = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level:<8}</level> | "
        "<cyan>{extra[rel_path]}</cyan>[<cyan>{line}</cyan>] "
        "(<cyan>{function}</cyan>) ----> <level>{message}</level>\n"
    )
    return result


logger.remove()
logger.add(
    sys.stdout,
    format=format_record,
    level=settings.logger.log_level,
    backtrace=True,
    diagnose=True,
    enqueue=True,
)
