# 5-minute local setup

## 1. Get a Gemini API key

Create a Gemini API key in Google AI Studio. Keep it private.

## 2. Install

```bash
cd skills/ecommerce-creative-intelligence
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Configure

Copy `.env.example` to `.env` and set `GEMINI_API_KEY`.

The app intentionally does not read `.env` automatically. Export it in the shell or use your normal environment manager:

```bash
export GEMINI_API_KEY="your-key"
```

## 4. Launch the browser UI

```bash
streamlit run app.py
```

Open the local URL shown by Streamlit, upload a product image, select platform/languages, and click **开始生成**.

## 5. CLI alternative

```bash
PYTHONPATH=. python -m runtime.cli \
  --product "Cloth Napkins" \
  --category "Kitchen / Dining" \
  --image /absolute/path/to/product.jpg \
  --platform "TikTok Shop" \
  --market US \
  --languages English,Japanese,Chinese \
  --count 8 \
  --research
```

## What it produces

- Product Master
- current public-web creative research with Google Search grounding
- Creative Analysis
- Creative Gap
- Creative Strategy
- 6–8 image plan
- multilingual copy master
- image prompts
- generated images
- QC report

Generated assets are written under `outputs/ecommerce/`, which is ignored by Git.

## Important

Public-web research is not the same as private TikTok Shop seller analytics. The system must not invent GMV, sales, rankings, or conversion metrics. Add an official/authorized data provider later through `MarketResearchProvider` when those metrics are available.
