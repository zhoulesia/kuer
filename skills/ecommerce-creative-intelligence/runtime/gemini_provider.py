"""Gemini-backed providers for the e-commerce creative pipeline.

Uses the official google-genai SDK. No API key is stored in source code;
set GEMINI_API_KEY in the environment.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from google import genai
from google.genai import types


TEXT_MODEL = os.getenv("GEMINI_TEXT_MODEL", "gemini-3.6-flash")
IMAGE_MODEL = os.getenv("GEMINI_IMAGE_MODEL", "gemini-3.1-flash-image")


class GeminiClient:
    def __init__(self, api_key: str | None = None):
        key = api_key or os.getenv("GEMINI_API_KEY")
        if not key:
            raise RuntimeError("GEMINI_API_KEY is not configured")
        self.client = genai.Client(api_key=key)

    @staticmethod
    def _json(text: str) -> dict[str, Any]:
        text = text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            text = text.rsplit("```", 1)[0]
        return json.loads(text)

    def text_json(self, prompt: str, *, web_search: bool = False) -> dict[str, Any]:
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2,
        )
        if web_search:
            config.tools = [types.Tool(google_search=types.GoogleSearch())]
        response = self.client.models.generate_content(
            model=TEXT_MODEL,
            contents=prompt,
            config=config,
        )
        return self._json(response.text)

    def vision_json(self, image_paths: list[str], prompt: str) -> dict[str, Any]:
        contents: list[Any] = [prompt]
        for raw_path in image_paths[:10]:
            path = Path(raw_path)
            if not path.exists():
                continue
            mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
            contents.append(types.Part.from_bytes(data=path.read_bytes(), mime_type=mime))
        return self._json(
            self.client.models.generate_content(
                model=TEXT_MODEL,
                contents=contents,
                config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.1),
            ).text
        )

    def generate_image(self, prompt: str, *, reference_images: list[str], aspect_ratio: str) -> str:
        contents: list[Any] = [prompt]
        for raw_path in reference_images[:10]:
            path = Path(raw_path)
            if not path.exists():
                continue
            mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
            contents.append(types.Part.from_bytes(data=path.read_bytes(), mime_type=mime))

        response = self.client.models.generate_content(
            model=IMAGE_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(aspect_ratio=aspect_ratio),
            ),
        )
        for part in response.parts:
            if getattr(part, "inline_data", None) is not None:
                image = part.as_image()
                output_dir = Path(os.getenv("ECOMMERCE_OUTPUT_DIR", "outputs/ecommerce"))
                output_dir.mkdir(parents=True, exist_ok=True)
                name = f"creative_{len(list(output_dir.glob('creative_*.png')))+1:02d}.png"
                output = output_dir / name
                image.save(output)
                return str(output)
        raise RuntimeError("Gemini image generation returned no image")


class GeminiCreativeModelProvider:
    def __init__(self, client: GeminiClient):
        self.client = client

    def complete(self, task: str, payload: dict[str, Any]) -> dict[str, Any]:
        prompt = f"""
You are the senior e-commerce creative director for a production system.
Task: {task}

Rules:
- Never invent product dimensions, materials, components, certifications, performance metrics, or claims.
- Preserve the exact product identity from the supplied Product Master / product images.
- Use market research only for abstract patterns and opportunities; never copy a competitor's exact image, text, logo, or unique composition.
- Return ONLY valid JSON.

Payload:
{json.dumps(payload, ensure_ascii=False, default=str)}
"""
        return self.client.text_json(prompt)


class GeminiProductVisionProvider:
    def __init__(self, client: GeminiClient):
        self.client = client

    def analyze(self, request: dict[str, Any]) -> dict[str, Any]:
        images = request.get("product_images", [])
        if not images:
            return {"status": "no_images", "unknowns": ["No product image supplied"]}
        return self.client.vision_json(images, """
Analyze the supplied product images for an e-commerce production workflow.
Return JSON with: appearance, structure, component_count, visual_identity,
dimensions_visible, selling_points_visible, angle_inventory, unknowns, forbidden_changes.
Only report facts visibly supported by the images. Never infer hidden dimensions or components.
""")


class GeminiImageGenerationProvider:
    def __init__(self, client: GeminiClient):
        self.client = client

    def generate(self, request: dict[str, Any]) -> list[dict[str, Any]]:
        platform = request.get("platform", {})
        ratio = platform.get("aspect_ratio") or ("9:16" if "tiktok" in platform.get("name", "").lower() else "1:1")
        references = request.get("product_master", {}).get("source_images", []) or request.get("reference_images", [])
        results = []
        for index, prompt in enumerate(request.get("prompts", []), start=1):
            text = prompt.get("prompt", prompt) if isinstance(prompt, dict) else str(prompt)
            path = self.client.generate_image(text, reference_images=references, aspect_ratio=ratio)
            results.append({"id": index, "status": "generated", "path": path, "aspect_ratio": ratio})
        return results


class GeminiMarketResearchProvider:
    def __init__(self, client: GeminiClient):
        self.client = client

    def search(self, request: dict[str, Any]):
        from .contracts import ResearchResult
        product = request.get("product", {})
        platform = request.get("platform", {})
        count = request.get("research", {}).get("competitor_count", 10)
        prompt = f"""
Research the current e-commerce creative landscape for this product category.
Platform: {platform}
Product: {product}
Target roughly {count} relevant public examples. Focus on observable creative patterns:
hero image conventions, scene types, benefit messaging, visual hierarchy, recurring claims,
review themes, and whitespace opportunities. Do not claim sales/GMV/ranking unless a source
explicitly supports it. Return JSON: {{"products":[], "patterns":[], "gaps":[], "sources":[]}}.
"""
        data = self.client.text_json(prompt, web_search=True)
        return ResearchResult(
            products=data.get("products", []),
            source="Gemini Google Search grounding",
            data_quality="grounded_web_research",
            limitations=data.get("sources", []),
        )
