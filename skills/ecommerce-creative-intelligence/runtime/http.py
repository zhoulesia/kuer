"""Minimal HTTP adapter contract; wire into FastAPI/Flask/etc. in the host app."""
from typing import Any
from .pipeline import CreativePipeline


def ecommerce_creative_endpoint(payload: dict[str, Any], pipeline: CreativePipeline) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("request body must be an object")
    if "product" not in payload or "platform" not in payload or "languages" not in payload:
        raise ValueError("product, platform, and languages are required")
    return pipeline.run(payload)
