"""用本地 gsuid_core(pytakumi)真实渲染管线出图验证。

用法（用核心的 venv 跑）：
    D:/122/bot/gsuid_core/.venv/Scripts/python.exe tests/render_with_gsuid.py
"""

import sys
import asyncio
import importlib
import types
from pathlib import Path

CORE = Path(r"D:\122\bot\gsuid_core")
PLUGIN = Path(__file__).resolve().parent.parent
OUT = PLUGIN / "tests" / "gsuid_out"

sys.path.insert(0, str(CORE))

# 绕过 __init__.py，直接加载子模块
pkg = types.ModuleType("WWBetaDiff")
pkg.__path__ = [str(PLUGIN)]
sys.modules["WWBetaDiff"] = pkg
api = importlib.import_module("WWBetaDiff.api")
render = importlib.import_module("WWBetaDiff.render")


async def main() -> None:
    OUT.mkdir(exist_ok=True)
    versions, diffs = await api.get_beta_diffs()
    items = api.merge_items(diffs)
    print("版本:", versions, "| 条目数:", len(items))

    overview = await render.render_overview(versions, items)
    (OUT / "overview.png").write_bytes(overview)
    print("overview:", len(overview), "bytes")

    item = next(i for i in items if i["entity"] == "character")
    detail = await render.render_detail(versions, item)
    (OUT / f"detail_{item['name']}.png").write_bytes(detail)
    print("detail:", item["name"], len(detail), "bytes")


asyncio.run(main())
