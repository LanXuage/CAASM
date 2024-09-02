#!/bin/env python3
import logging


from uvicorn.config import LOGGING_CONFIG
from settings import LOGGER_FORMATTER, ACCESS_LOGGER_FORMATTER

logger = logging.getLogger("uvicorn.error")
stream_handler = logging.StreamHandler()

stream_handler.setFormatter(
    logging.Formatter(
        fmt=LOGGER_FORMATTER.replace("%(levelprefix)s", "%(levelname)s:    ")
    )
)
logger.setLevel(logging.INFO)
logger.addHandler(stream_handler)

LOGGING_CONFIG["formatters"]["default"]["fmt"] = LOGGER_FORMATTER
LOGGING_CONFIG["formatters"]["access"]["fmt"] = ACCESS_LOGGER_FORMATTER