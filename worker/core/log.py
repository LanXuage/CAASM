#!/bin/env python3
import logging

from settings import CAASM_LOGGER_FORMATTER


logger = logging.getLogger("worker.error")
stream_handler = logging.StreamHandler()

stream_handler.setFormatter(
    logging.Formatter(
        fmt=CAASM_LOGGER_FORMATTER.replace("%(levelprefix)s", "%(levelname)s:    ")
    )
)
logger.setLevel(logging.INFO)
logger.addHandler(stream_handler)
