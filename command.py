import httpx

from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event

from .api import find_item, merge_items, get_beta_diffs
from .render import render_detail, render_overview

sv = SV("鸣潮体验服差异", area="ALL")


@sv.on_command("ng", block=True)
async def ww_ng(bot: Bot, ev: Event) -> None:
    try:
        versions, diffs = await get_beta_diffs()
    except (httpx.HTTPError, ValueError, KeyError):
        await bot.send("鸣潮体验服差异数据暂时不可用，请稍后重试。")
        return

    items = merge_items(diffs)
    query = ev.text.strip()
    if not query:
        await bot.send(await render_overview(versions, items))
        return

    item = find_item(items, query)
    if item is None:
        names = "、".join(entry["name"] for entry in items)
        await bot.send(f"未找到“{query}”。当前可查询：{names}")
        return
    await bot.send(await render_detail(versions, item))
