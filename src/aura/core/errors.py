from __future__ import annotations


class AuraError(Exception):
    """Base exception for all Aura errors."""

    def __init__(self, message: str = "", *args: object) -> None:
        self.message = message
        super().__init__(message, *args)

    def __str__(self) -> str:
        return self.message


class ConfigurationError(AuraError):
    """Raised when configuration is invalid or missing."""


class DatabaseError(AuraError):
    """Raised for database connection or query failures."""


class InfrastructureError(AuraError):
    """Raised for infrastructure-level failures (network, filesystem, etc.)."""


class ApplicationError(AuraError):
    """Raised for application-level business logic errors."""


class ValidationError(AuraError):
    """Raised when input validation fails."""


class ProviderError(AuraError):
    """Raised when an LLM provider operation fails."""
