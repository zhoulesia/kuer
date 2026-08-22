# E-Commerce Creative Intelligence

This module provides the orchestration contract for research-driven e-commerce creative generation.

## Runtime flow

`input -> research -> product master -> creative analysis -> creative gap -> strategy -> image plan -> copy -> prompts -> image provider -> QC`

## Provider boundary

Implement platform/data providers and image providers behind adapters. The core skill must not assume a particular scraping vendor or image model.

### Recommended adapters

- `MarketResearchProvider`
- `ProductImageProvider`
- `ImageGenerationProvider`
- `TranslationProvider` (optional)

## Safety and accuracy

Research data must preserve provenance and data quality. Unknown metrics stay unknown. Competitor assets are analyzed for patterns, not copied.
