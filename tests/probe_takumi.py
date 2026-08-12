"""pytakumi 特性探测：测试 inline 背景、padding、border 等在真实渲染器下的支持情况。"""

import sys
import asyncio
from pathlib import Path

CORE = Path(r"D:\122\bot\gsuid_core")
OUT = Path(__file__).resolve().parent / "gsuid_out"
sys.path.insert(0, str(CORE))

from gsuid_core.utils.html_render import render_html_to_bytes  # noqa: E402

HTML = """
<html><head><meta charset="utf-8"><style>
body { width: 900px; font-family: 'MiSans', sans-serif; background: #fff; padding: 20px; font-size: 24px; }
div { margin-bottom: 16px; }
.a span { background: #fbc4cc; color: #8f1d2c; font-weight: bold; border-radius: 6px; padding: 0 6px; }
.b span { background: #a9e8c3; color: #0f5c2e; font-weight: bold; }
.c span { color: #d6336c; font-weight: bold; border-bottom: 3px solid #f28b9b; }
.d span { color: #d6336c; font-weight: bold; text-decoration: underline; }
.e .tag { display: inline-block; background: #f28b9b; color: #fff; border-radius: 12px; padding: 2px 12px; font-size: 18px; }
.f .tag { background: #f28b9b; color: #fff; border-radius: 12px; padding: 2px 12px; font-size: 18px; }
.g mark { background: #fbc4cc; font-weight: bold; }
</style></head><body>
<div class="a">A span背景+padding+圆角: 伤害倍率提升<span>60</span>%持续30秒</div>
<div class="b">B span背景无padding: 伤害倍率提升<span>60</span>%持续30秒</div>
<div class="c">C 彩色加粗+下边框: 伤害倍率提升<span>60</span>%持续30秒</div>
<div class="d">D 彩色加粗+下划线: 伤害倍率提升<span>60</span>%持续30秒</div>
<div class="e"><span class="tag">旧</span>E inline-block标签</div>
<div class="f"><span class="tag">新</span>F inline标签</div>
<div class="g">G mark标签: 伤害倍率提升<mark>60</mark>%持续30秒</div>
</body></html>
"""


async def main() -> None:
    OUT.mkdir(exist_ok=True)
    data = await render_html_to_bytes(HTML, max_width=900, dpi=96, lang="zh")
    (OUT / "probe.png").write_bytes(data)
    print("saved", len(data))


asyncio.run(main())
