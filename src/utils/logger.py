# TODO: Implement logging project-wide

import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
import inspect


class Logger:
    def __init__(self):
        logs_path = Path.home() / ".moves" / "logs"
        logs_path.mkdir(parents=True, exist_ok=True)

        try:
            stack = inspect.stack()
            caller_frame = stack[1]
            caller_filename = caller_frame.filename
            module_name = Path(caller_filename).stem
        except Exception:
            module_name = "main"

        logger = logging.getLogger(f"moves.{module_name}")
        if not logger.handlers:
            logger.setLevel(logging.INFO)
            handler = RotatingFileHandler(
                logs_path / f"{module_name}.log",
                maxBytes=5 * 1024 * 1024,
                backupCount=5,
                encoding="utf-8",
            )
            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s | %(levelname)s | %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
            )
            logger.addHandler(handler)
            logger.propagate = False
        self._logger = logger

    def info(self, msg):
        self._logger.info(msg)

    def error(self, msg):
        self._logger.error(msg)


if __name__ == "__main__":
    logger = Logger()
    logger.info("This is an info message.")
    logger.error("This is an error message.")
