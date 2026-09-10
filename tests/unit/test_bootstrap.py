from __future__ import annotations

import pytest

from aura.application.bootstrap import AuraApplication, create_application
from aura.core.config import AuraSettings, DatabaseSettings, LoggingSettings
from aura.core.errors import ConfigurationError


class TestAuraApplication:
    @pytest.fixture
    def app_settings(self) -> AuraSettings:
        return AuraSettings(
            environment="testing",
            debug=True,
            database=DatabaseSettings(),
            logging=LoggingSettings(level="DEBUG"),
        )

    def test_create_application(self, app_settings: AuraSettings) -> None:
        app = AuraApplication(app_settings)
        assert app.settings.environment == "testing"
        assert app.is_started is False

    def test_create_application_factory(self) -> None:
        app = create_application(AuraSettings(environment="testing"))
        assert isinstance(app, AuraApplication)

    def test_db_access_before_startup_raises(self, app_settings: AuraSettings) -> None:
        app = AuraApplication(app_settings)
        with pytest.raises(ConfigurationError):
            _ = app.db
