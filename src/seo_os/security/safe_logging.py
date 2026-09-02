"""Logging configuration that redacts message text and structured arguments."""

from __future__ import annotations

import logging
from typing import Any

from .redaction import redact_mapping, redact_text


class SafeLogFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = redact_text(record.msg)
        else:
            record.msg = redact_mapping(record.msg)
        if record.args:
            if isinstance(record.args, tuple):
                record.args = tuple(redact_mapping(value) for value in record.args)
            else:
                record.args = redact_mapping(record.args)
        return True


class SafeFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return redact_text(super().format(record))


def configure_safe_logging(level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger("seo_os")
    logger.setLevel(level)
    logger.propagate = False
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.addFilter(SafeLogFilter())
        handler.setFormatter(SafeFormatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
        logger.addHandler(handler)
    return logger
