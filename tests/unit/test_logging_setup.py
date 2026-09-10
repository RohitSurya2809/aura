from __future__ import annotations

import logging

from aura.core.config import LoggingSettings
from aura.core.logging import get_logger, setup_logging


class TestLoggingSetup:
    def test_setup_console_logging(self) -> None:
        settings = LoggingSettings(level="DEBUG", format="console")
        setup_logging(settings)
        root = logging.getLogger()
        assert root.level == logging.DEBUG
        assert len(root.handlers) > 0

    def test_setup_json_logging(self) -> None:
        settings = LoggingSettings(level="INFO", format="json")
        setup_logging(settings)
        root = logging.getLogger()
        assert root.level == logging.INFO

    def test_get_logger_returns_bound_logger(self) -> None:
        settings = LoggingSettings()
        setup_logging(settings)
        log = get_logger("test")
        assert log is not None

    def test_noisy_loggers_suppressed(self) -> None:
        settings = LoggingSettings(level="DEBUG")
        setup_logging(settings)
        for name in ("asyncio", "sqlalchemy.engine", "alembic"):
            assert logging.getLogger(name).level >= logging.WARNING
