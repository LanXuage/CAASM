#!/bin/env python3
import logging


from uvicorn.config import LOGGING_CONFIG
from settings import CAASM_LOGGER_FORMATTER, CAASM_ACCESS_LOGGER_FORMATTER

logger = logging.getLogger("uvicorn.error")
stream_handler = logging.StreamHandler()

stream_handler.setFormatter(
    logging.Formatter(
        fmt=CAASM_LOGGER_FORMATTER.replace("%(levelprefix)s", "%(levelname)s:    ")
    )
)
logger.setLevel(logging.INFO)
logger.addHandler(stream_handler)

LOGGING_CONFIG["formatters"]["default"]["fmt"] = CAASM_LOGGER_FORMATTER
LOGGING_CONFIG["formatters"]["access"]["fmt"] = CAASM_ACCESS_LOGGER_FORMATTER