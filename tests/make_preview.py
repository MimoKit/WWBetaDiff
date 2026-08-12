"""本地预览脚本：不依赖 gsuid_core，用 playwright 把 render.py 生成的 HTML 截图。

用法（用装了 playwright 的 python 跑）：
    python tests/make_preview.py
"""

import sys
import asyncio
from pathlib import Path
from unittest.mock import MagicMock

PLUGIN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLUGIN.parent))  # 让 "import WWBetaDiff" 形式的包导入可用

captured: dict[str, str] = {}


async def fake_render(html: str, **kwargs) -> bytes:
    captured["html"] = html
    return b""


# 打桩 gsuid_core，让 render.py 可以不装框架直接 import
hr = MagicMock()
hr.render_html_to_bytes = fake_render
sys.modules["gsuid_core"] = MagicMock()
sys.modules["gsuid_core.utils"] = MagicMock()
sys.modules["gsuid_core.utils.html_render"] = hr

# 绕过 __init__.py（依赖 gsuid_core.sv），构造空包后直接加载子模块
import importlib
import types

pkg = types.ModuleType("WWBetaDiff")
pkg.__path__ = [str(PLUGIN)]
sys.modules["WWBetaDiff"] = pkg
render = importlib.import_module("WWBetaDiff.render")

VERSIONS = ["2.6.52", "2.6.53", "2.6.54"]

LONG_BEFORE = "施放共鸣技能时，回复自身15点协奏能量，并使队伍中所有角色攻击力提升20%，持续30秒。"
LONG_AFTER = "施放共鸣技能时，回复自身20点协奏能量，并使队伍中所有角色攻击力提升25%，持续30秒。"


def make_items():
    stage1 = {
        "changes": [
            {"section": "profile", "key": "profile.name", "labelKey": "name",
             "context": "基础资料", "before": "景燃", "after": "景燃·改"},
            {"section": "stats", "key": "stats.90.atk", "labelKey": "atk",
             "context": "满级属性", "before": "攻击力 412", "after": "攻击力 437"},
            {"section": "skills", "key": "skill.1.level.10.row.倍率.value",
             "labelKey": "value", "context": "共鸣技能 · 掠火",
             "before": "造成 220% 热熔伤害", "after": "造成 268% 热熔伤害"},
            {"section": "forte", "key": "forte.1.description", "labelKey": "description",
             "context": "固有技能 · 焰心", "before": LONG_BEFORE, "after": LONG_AFTER},
        ]
    }
    stage2 = {
        "changes": [
            {"section": "chains", "key": "chains.2.description", "labelKey": "description",
             "context": "共鸣链 · 二链", "before": "暴击率提升8%", "after": "暴击率提升12%"},
        ]
    }
    item = {"id": "1212", "entity": "character", "name": "景燃", "rarity": 5,
            "stages": [stage1, stage2]}
    weapon = {"id": "3301", "entity": "weapon", "name": "焰痕之剑", "rarity": 5,
              "stages": [None, {"changes": []}]}
    return item, [item, weapon]


async def main():
    item, items = make_items()
    out = PLUGIN / "tests" / "preview"
    out.mkdir(exist_ok=True)

    await render.render_overview(VERSIONS, items)
    (out / "overview.html").write_text(captured["html"], encoding="utf-8")
    await render.render_detail(VERSIONS, item)
    (out / "detail.html").write_text(captured["html"], encoding="utf-8")

    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": render.WIDTH + 80, "height": 900},
            device_scale_factor=2,
        )
        for name in ("overview", "detail"):
            await page.goto((out / f"{name}.html").as_uri())
            await page.wait_for_timeout(800)
            await page.screenshot(path=str(out / f"{name}.png"), full_page=True)
        await browser.close()
    print("done:", out)


asyncio.run(main())
