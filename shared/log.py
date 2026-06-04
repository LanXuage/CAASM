#!/bin/env python3
import logging


def get_logger(name: str, formatter: str) -> logging.Logger:
    """Create a configured logger with the given name and formatter pattern.

    The formatter pattern may contain '%(levelprefix)s' which will be
    replaced by '%(levelname)s:    ' for consistency with uvicorn.
    """
    logger = logging.getLogger(name)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(
        logging.Formatter(
            fmt=formatter.replace("%(levelprefix)s", "%(levelname)s:    ")
        )
    )
    logger.setLevel(logging.INFO)
    logger.addHandler(stream_handler)
    return logger