"""探测3：tag 胶囊在正文行内的表现。"""

import sys
import asyncio
from pathlib import Path

CORE = Path(r"D:\122\bot\gsuid_core")
OUT = Path(__file__).resolve().parent / "gsuid_out"
sys.path.insert(0, str(CORE))

from gsuid_core.utils.html_render import render_html_to_bytes  # noqa: E402

HTML = """
<html><head><meta charset="utf-8"><style>
body { width: 600px; font-family: 'MiSans', sans-serif; background: #fff; padding: 20px; }
.row { border-radius: 12px; padding: 10px 14px; font-size: 21px; line-height: 1.65; background: #fdeeee; color: #b0434f; margin-bottom: 14px; }
.t1 { display: inline-block; font-size: 15px; border-radius: 999px; padding: 0 12px; margin-right: 10px; color: #fff; background: #f28b9b; }
.t2 { display: inline-block; font-size: 17px; border-radius: 8px; padding: 2px 10px; margin-right: 10px; color: #fff; background: #f28b9b; line-height: 1.2; }
.t3 { font-weight: bold; color: #d6336c; margin-right: 8px; }
</style></head><body>
<div class="row"><span class="t1">旧</span>T1 原方案 15px/999px/padding 0 12px</div>
<div class="row"><span class="t2">旧</span>T2 17px/圆角8/line-height 1.2</div>
<div class="row"><span class="t3">旧 ·</span>T3 纯文字加粗变色</div>
</body></html>
"""


async def main() -> None:
    data = await render_html_to_bytes(HTML, max_width=600, dpi=96, lang="zh")
    (OUT / "probe3.png").write_bytes(data)
    print("saved", len(data))


asyncio.run(main())
