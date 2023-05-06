import sys

from loguru import logger as log
from stela import settings


class Setup:
    def __init__(self) -> None:
        self.log_level = settings.get("project.log_level", "INFO")

        log.remove()
        log.add(sys.stderr, level=self.log_level)

        log.debug(f"Setup ready")
