"""探测2：inline-block 长文本是否换行/溢出。"""

import sys
import asyncio
from pathlib import Path

CORE = Path(r"D:\122\bot\gsuid_core")
OUT = Path(__file__).resolve().parent / "gsuid_out"
sys.path.insert(0, str(CORE))

from gsuid_core.utils.html_render import render_html_to_bytes  # noqa: E402

HTML = """
<html><head><meta charset="utf-8"><style>
body { width: 500px; font-family: 'MiSans', sans-serif; background: #fff; padding: 20px; font-size: 24px; }
div { margin-bottom: 20px; line-height: 1.6; }
.hl { display: inline-block; background: #fbc4cc; color: #8f1d2c; font-weight: bold; border-radius: 6px; }
.hl2 { display: inline-block; background: #a9e8c3; color: #0f5c2e; font-weight: bold; }
</style></head><body>
<div>每次进入战斗时，景燃获得下述效果，每4秒可触发1次。<span class="hl">若景燃持有的【鬼护】不足25点，补充至25点。</span>景燃获得通幽。通幽状态下重击伤害加深。</div>
<div>短标记<span class="hl2">80%</span>测试换行是否正常，后面再接一段普通文字看看排版效果会不会坏掉。</div>
</body></html>
"""


async def main() -> None:
    data = await render_html_to_bytes(HTML, max_width=500, dpi=96, lang="zh")
    (OUT / "probe2.png").write_bytes(data)
    print("saved", len(data))


asyncio.run(main())
