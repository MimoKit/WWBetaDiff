"""真实数据预览：拉取 nanoka.cc 的真实差异数据，渲染总览 + 前两个角色的详情图。"""

import sys
import asyncio
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import MagicMock

PLUGIN = Path(__file__).resolve().parent.parent
OUT = PLUGIN / "tests" / f"preview_{datetime.now():%H%M%S}"

captured: dict[str, str] = {}


async def fake_render(html: str, **kwargs) -> bytes:
    captured["html"] = html
    return b""


# 打桩 gsuid_core（html_render + data_store）
hr = MagicMock()
hr.render_html_to_bytes = fake_render
ds = MagicMock()
ds.get_res_path.return_value = Path(tempfile.gettempdir()) / "wwbetadiff_preview"
sys.modules["gsuid_core"] = MagicMock()
sys.modules["gsuid_core.utils"] = MagicMock()
sys.modules["gsuid_core.utils.html_render"] = hr
sys.modules["gsuid_core.data_store"] = ds

import importlib
import types

pkg = types.ModuleType("WWBetaDiff")
pkg.__path__ = [str(PLUGIN)]
sys.modules["WWBetaDiff"] = pkg
api = importlib.import_module("WWBetaDiff.api")
render = importlib.import_module("WWBetaDiff.render")


async def main():
    ds.get_res_path.return_value.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    versions, diffs = await api.get_beta_diffs()
    items = api.merge_items(diffs)
    print("版本:", versions, "| 条目:", [i["name"] for i in items])

    await render.render_overview(versions, items)
    (OUT / "real_overview.html").write_text(captured["html"], encoding="utf-8")

    targets = [i for i in items if i["entity"] == "character"][:2] or items[:1]
    detail_names = []
    for item in targets:
        await render.render_detail(versions, item)
        name = f"real_detail_{item['name']}"
        (OUT / f"{name}.html").write_text(captured["html"], encoding="utf-8")
        detail_names.append(name)

    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": render.WIDTH + 80, "height": 900},
            device_scale_factor=2,
        )
        for name in ["real_overview", *detail_names]:
            await page.goto((OUT / f"{name}.html").as_uri())
            await page.wait_for_timeout(800)
            await page.screenshot(path=str(OUT / f"{name}.png"), full_page=True)
        await browser.close()
    print("done:", OUT)


asyncio.run(main())
