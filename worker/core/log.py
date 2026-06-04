#!/bin/env python3
import logging

from settings import CAASM_LOGGER_FORMATTER
from shared.log import get_logger

logger = get_logger("worker.error", CAASM_LOGGER_FORMATTER)

# Also configure shared.nebula logger to use the same handler style
logging.getLogger("shared.nebula").handlers = logger.handlers[:]
logging.getLogger("shared.nebula").setLevel(logging.INFO)