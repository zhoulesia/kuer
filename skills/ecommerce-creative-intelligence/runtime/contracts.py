"""Provider contracts. Implement these against your chosen APIs/models."""
from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class ResearchResult:
    products: list[dict[str, Any]] = field(default_factory=list)
    source: str = ""
    data_quality: str = "unknown"
    limitations: list[str] = field(default_factory=list)


class MarketResearchProvider(Protocol):
    def search(self, request: dict[str, Any]) -> ResearchResult: ...


class ProductVisionProvider(Protocol):
    def analyze(self, request: dict[str, Any]) -> dict[str, Any]: ...


class ImageGenerationProvider(Protocol):
    def generate(self, request: dict[str, Any]) -> list[dict[str, Any]]: ...


class CreativeModelProvider(Protocol):
    def complete(self, task: str, payload: dict[str, Any]) -> dict[str, Any]: ...
