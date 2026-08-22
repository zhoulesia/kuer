"""Safe defaults: no silent fake data. Replace with real integrations."""
from .contracts import ResearchResult


class DisabledMarketResearchProvider:
    def search(self, request):
        return ResearchResult(
            products=[],
            source="disabled",
            data_quality="unavailable",
            limitations=["No market-data provider configured; performance metrics were not fabricated."],
        )


class PassthroughProductVisionProvider:
    def analyze(self, request):
        return {"status": "requires_provider", "product_images": request.get("product_images", [])}


class ModelCreativeProvider:
    def __init__(self, model):
        self.model = model

    def complete(self, task, payload):
        return self.model(task=task, payload=payload)


class DisabledImageGenerationProvider:
    def generate(self, request):
        return [{"status": "requires_provider", "prompt": p} for p in request.get("prompts", [])]
