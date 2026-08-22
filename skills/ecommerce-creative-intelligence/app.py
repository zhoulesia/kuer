"""Local browser UI for the e-commerce creative generator.
Run: streamlit run app.py
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import streamlit as st

from runtime.gemini_provider import (
    GeminiClient,
    GeminiCreativeModelProvider,
    GeminiImageGenerationProvider,
    GeminiMarketResearchProvider,
    GeminiProductVisionProvider,
)
from runtime.pipeline import CreativePipeline


st.set_page_config(page_title="E-commerce Creative Studio", layout="wide")
st.title("E-commerce Creative Studio")
st.caption("产品图 → 爆款研究 → 8张图策略 → 多语言文案 → 图片生成 → QC")

with st.sidebar:
    platform = st.selectbox("平台", ["TikTok Shop", "Amazon", "Instagram", "Shopify"])
    market = st.text_input("市场", "US")
    languages = st.multiselect("语言", ["English", "Japanese", "Chinese"], ["English"])
    count = st.slider("图片数量", 6, 8, 8)
    research = st.checkbox("分析当前爆款/市场视觉", True)

product_name = st.text_input("产品名称", placeholder="例如：Cloth Napkins")
category = st.text_input("产品类别", placeholder="例如：Kitchen / Dining")
images = st.file_uploader("上传产品图（可多张）", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True)

if st.button("开始生成", type="primary", disabled=not product_name or not images):
    with tempfile.TemporaryDirectory() as temp_dir:
        paths = []
        for i, upload in enumerate(images):
            suffix = Path(upload.name).suffix or ".png"
            path = Path(temp_dir) / f"product_{i}{suffix}"
            path.write_bytes(upload.getvalue())
            paths.append(str(path))

        request = {
            "product": {"name": product_name, "category": category},
            "product_images": paths,
            "platform": {
                "name": platform,
                "market": market,
                "aspect_ratio": "9:16" if platform == "TikTok Shop" else ("1:1" if platform == "Amazon" else "4:5"),
            },
            "languages": languages or ["English"],
            "image_count": count,
            "research": {"enabled": research, "competitor_count": 10},
        }

        with st.status("正在执行完整电商创意流程…", expanded=True) as status:
            try:
                client = GeminiClient()
                pipeline = CreativePipeline(
                    research=GeminiMarketResearchProvider(client),
                    vision=GeminiProductVisionProvider(client),
                    creative=GeminiCreativeModelProvider(client),
                    image_generation=GeminiImageGenerationProvider(client),
                )
                result = pipeline.run(request)
                status.update(label="完成", state="complete")
            except Exception as exc:
                status.update(label="失败", state="error")
                st.exception(exc)
                st.stop()

        st.subheader("生成结果")
        generated = result.get("generated_images", [])
        cols = st.columns(2)
        for i, item in enumerate(generated):
            path = item.get("path")
            if path and Path(path).exists():
                cols[i % 2].image(path, caption=f"第 {i + 1} 张")

        with st.expander("查看 Creative Strategy / Image Plan / Copy / QC"):
            st.json({
                "creative_strategy": result.get("creative_strategy"),
                "image_plan": result.get("image_plan"),
                "copy_master": result.get("copy_master"),
                "qc_report": result.get("qc_report"),
            })

        Path("outputs/ecommerce").mkdir(parents=True, exist_ok=True)
        Path("outputs/ecommerce/result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        st.success("已保存到 outputs/ecommerce/result.json")
