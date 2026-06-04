#!/bin/env python3
import logging

from uvicorn.config import LOGGING_CONFIG
from settings import CAASM_LOGGER_FORMATTER, CAASM_ACCESS_LOGGER_FORMATTER
from shared.log import get_logger

logger = get_logger("uvicorn.error", CAASM_LOGGER_FORMATTER)

# Configure uvicorn access log format
LOGGING_CONFIG["formatters"]["default"]["fmt"] = CAASM_LOGGER_FORMATTER
LOGGING_CONFIG["formatters"]["access"]["fmt"] = CAASM_ACCESS_LOGGER_FORMATTER

# Also configure shared.nebula logger to use the same handler style
logging.getLogger("shared.nebula").handlers = logger.handlers[:]
logging.getLogger("shared.nebula").setLevel(logging.INFO)