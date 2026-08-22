# Runtime integration

The runtime is deliberately framework- and vendor-neutral.

## Execution contract

```python
from skills.ecommerce_creative_intelligence.runtime.pipeline import CreativePipeline

result = pipeline.run({
    "product": {"name": "Cloth Napkins", "category": "napkins"},
    "product_images": ["..."],
    "platform": {"name": "TikTok Shop", "market": "US", "aspect_ratio": "9:16"},
    "languages": ["English", "Japanese"],
    "image_count": 8,
    "research": {"enabled": True, "competitor_count": 30}
})
```

## Required providers

1. MarketResearchProvider
2. ProductVisionProvider
3. CreativeModelProvider
4. ImageGenerationProvider

The included disabled providers intentionally return `requires_provider` / `unavailable` rather than pretending that data or images exist.

## HTTP

Use `ecommerce_creative_endpoint(payload, pipeline)` from your host web framework. It validates the minimum request shape and delegates to the pipeline.
