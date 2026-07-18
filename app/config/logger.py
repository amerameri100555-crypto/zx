from loguru import logger
import sys
from pathlib import Path

Path("app/logs").mkdir(parents=True, exist_ok=True)

logger.remove()

logger.add(
    sys.stdout,
    colorize=True,
    level="INFO"
)

logger.add(
    "app/logs/bot.log",
    rotation="10 MB",
    retention="30 days",
    encoding="utf-8",
    level="INFO"
)
