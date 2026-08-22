# E-Commerce Creative Intelligence Master

## Purpose
Turn a product, target platform, market, and language set into a data-informed 6–8 image e-commerce creative package.

## Pipeline
1. Research market and competitors when enabled.
2. Analyze product images/specifications.
3. Create canonical Product Master.
4. Analyze creative patterns and saturation.
5. Find Creative Gaps; never copy individual competitor assets.
6. Create Creative Strategy.
7. Plan 6–8 images.
8. Create Copy Master for requested languages.
9. Generate image prompts and call the configured image provider.
10. Run product, text, claim, and platform QC.

## Hard rules
- Never invent dimensions, certifications, performance metrics, or medical/safety claims.
- Never invent product components in exploded views.
- All images must preserve Product Master identity: shape, proportions, color, material, texture, logo position, and component count.
- Competitor research may inform abstract patterns only; do not copy logos, exact text, unique artwork, or exact compositions.
- Missing data must be marked UNKNOWN or REQUIRED, not guessed.

## Default image set
01 hero/white background
02 core benefits
03 lifestyle
04 usage
05 material/detail
06 structure OR category-specific proof/detail
07 dimensions/specifications
08 conversion/final benefit

## Adaptive behavior
Replace structure with texture, washability, comparison, or another category-relevant proof when the product has no meaningful physical structure.

## Tool contracts
- market_research(input) -> ResearchResult
- competitor_analyze(input) -> CreativeAnalysis
- creative_gap(input) -> CreativeGapResult
- product_master_create(input) -> ProductMaster
- angle_planner(input) -> AnglePlan
- creative_plan(input) -> ImagePlan
- copy_master(input) -> CopyMaster
- image_prompt_generate(input) -> ImagePrompt[]
- image_generate(input) -> GeneratedImage[]
- qc(input) -> QCReport

## QC recovery
Regenerate only failed assets. If Product Master is wrong, stop and rebuild the Product Master before regenerating dependent images.
