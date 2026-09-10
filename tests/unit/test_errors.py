from __future__ import annotations

import pytest

from aura.core.errors import (
    ApplicationError,
    AuraError,
    ConfigurationError,
    DatabaseError,
    InfrastructureError,
    ProviderError,
    ValidationError,
)


class TestErrorHierarchy:
    def test_base_error(self) -> None:
        err = AuraError("test message")
        assert str(err) == "test message"
        assert err.message == "test message"
        assert isinstance(err, Exception)

    def test_all_errors_inherit_from_aura_error(self) -> None:
        errors = [
            ConfigurationError("config"),
            DatabaseError("db"),
            InfrastructureError("infra"),
            ApplicationError("app"),
            ValidationError("validation"),
            ProviderError("provider"),
        ]
        for err in errors:
            assert isinstance(err, AuraError)

    def test_errors_are_catchable_by_base(self) -> None:
        with pytest.raises(AuraError):
            raise DatabaseError("connection failed")

    def test_error_message_preserved(self) -> None:
        err = ConfigurationError("missing API key")
        assert err.message == "missing API key"
        assert str(err) == "missing API key"
