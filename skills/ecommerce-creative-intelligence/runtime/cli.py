"""One-command CLI for generating an e-commerce creative package."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .gemini_provider import (
    GeminiClient,
    GeminiCreativeModelProvider,
    GeminiImageGenerationProvider,
    GeminiMarketResearchProvider,
    GeminiProductVisionProvider,
)
from .pipeline import CreativePipeline


def build_pipeline() -> CreativePipeline:
    client = GeminiClient()
    return CreativePipeline(
        research=GeminiMarketResearchProvider(client),
        vision=GeminiProductVisionProvider(client),
        creative=GeminiCreativeModelProvider(client),
        image_generation=GeminiImageGenerationProvider(client),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a 6-8 image e-commerce creative package")
    parser.add_argument("--product", required=True, help="Product name")
    parser.add_argument("--category", required=True, help="Product category")
    parser.add_argument("--image", action="append", default=[], help="Product image path; repeat for multiple images")
    parser.add_argument("--platform", default="TikTok Shop")
    parser.add_argument("--market", default="US")
    parser.add_argument("--ratio", default=None)
    parser.add_argument("--languages", default="English", help="Comma-separated: English,Japanese,Chinese")
    parser.add_argument("--count", type=int, default=8)
    parser.add_argument("--research", action="store_true")
    args = parser.parse_args()

    request = {
        "product": {"name": args.product, "category": args.category},
        "product_images": [str(Path(p)) for p in args.image],
        "platform": {"name": args.platform, "market": args.market, "aspect_ratio": args.ratio or ("9:16" if "tiktok" in args.platform.lower() else "1:1")},
        "languages": [x.strip() for x in args.languages.split(",") if x.strip()],
        "image_count": max(6, min(8, args.count)),
        "research": {"enabled": args.research, "competitor_count": 10},
    }
    result = build_pipeline().run(request)
    output = Path("outputs/ecommerce/result.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"Done. Result: {output}")
    for item in result.get("generated_images", []):
        print(item.get("path", item))


if __name__ == "__main__":
    main()
