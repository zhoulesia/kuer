"""Framework-neutral pipeline. Business logic stays provider-agnostic."""
from typing import Any
from .contracts import MarketResearchProvider, ProductVisionProvider, ImageGenerationProvider, CreativeModelProvider


class CreativePipeline:
    def __init__(self, *, research: MarketResearchProvider, vision: ProductVisionProvider,
                 creative: CreativeModelProvider, image_generation: ImageGenerationProvider):
        self.research = research
        self.vision = vision
        self.creative = creative
        self.image_generation = image_generation

    def run(self, request: dict[str, Any]) -> dict[str, Any]:
        research_result = self.research.search(request) if request.get("research", {}).get("enabled", True) else None
        product_master = self.creative.complete("product_master", {
            "request": request,
            "vision": self.vision.analyze(request),
        })
        creative_analysis = self.creative.complete("creative_analysis", {
            "research": research_result.__dict__ if research_result else None,
            "product_master": product_master,
        })
        creative_gap = self.creative.complete("creative_gap", {
            "creative_analysis": creative_analysis,
            "product_master": product_master,
        })
        strategy = self.creative.complete("creative_strategy", {
            "product_master": product_master,
            "creative_analysis": creative_analysis,
            "creative_gap": creative_gap,
            "platform": request.get("platform", {}),
        })
        image_plan = self.creative.complete("image_plan", {
            "strategy": strategy,
            "product_master": product_master,
            "count": request.get("image_count", 8),
        })
        copy_master = self.creative.complete("copy_master", {
            "strategy": strategy,
            "languages": request.get("languages", ["English"]),
            "product_master": product_master,
        })
        prompts = self.creative.complete("image_prompts", {
            "product_master": product_master,
            "strategy": strategy,
            "image_plan": image_plan,
            "copy_master": copy_master,
            "platform": request.get("platform", {}),
        })
        generated = self.image_generation.generate({
            "prompts": prompts,
            "product_master": product_master,
            "platform": request.get("platform", {}),
        })
        qc = self.creative.complete("qc", {
            "product_master": product_master,
            "generated_images": generated,
            "copy_master": copy_master,
            "platform": request.get("platform", {}),
        })
        return {
            "research": research_result.__dict__ if research_result else None,
            "product_master": product_master,
            "creative_analysis": creative_analysis,
            "creative_gap": creative_gap,
            "creative_strategy": strategy,
            "image_plan": image_plan,
            "copy_master": copy_master,
            "image_prompts": prompts,
            "generated_images": generated,
            "qc_report": qc,
        }
