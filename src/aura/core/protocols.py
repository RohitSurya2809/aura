from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, TypeVar, runtime_checkable

if TYPE_CHECKING:
    from uuid import UUID

T = TypeVar("T")


@runtime_checkable
class Repository(Protocol[T]):
    """Base repository interface for data access."""

    async def get_by_id(self, entity_id: UUID) -> T | None: ...
    async def create(self, entity: T) -> T: ...
    async def update(self, entity: T) -> T: ...
    async def delete(self, entity_id: UUID) -> bool: ...


@runtime_checkable
class LLMProvider(Protocol):
    """Abstract interface for LLM providers."""

    @property
    def provider_name(self) -> str: ...

    @property
    def is_available(self) -> bool: ...

    async def generate(self, prompt: str, **kwargs: object) -> str: ...
