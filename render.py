import re
import html
from typing import Any
from collections import defaultdict

from gsuid_core.utils.html_render import render_html_to_bytes

from .render_html import (
    WIDTH,
    page,
    header,
    footer,
    stage_block,
    group_title,
    render_change,
    overview_card,
)

MAX_CHANGES_PER_STAGE = 14
MAX_VALUE_LENGTH = 420

SECTION_NAMES = {
    "profile": "基础资料",
    "stats": "满级属性",
    "skills": "技能",
    "forte": "固有技能",
    "chains": "共鸣链",
    "refinement": "武器谐振",
}

LABEL_NAMES = {
    "name": "名称",
    "description": "描述",
    "simpleDescription": "技能说明",
    "skillName": "技能名称",
    "hp": "生命",
    "atk": "攻击",
    "def": "防御",
    "value": "倍率",
    "attribute": "属性",
}


def _plain_text(value: Any) -> str:
    if value is None or value == "":
        return "无"
    text = str(value).replace("<br />", "\n").replace("<br>", "\n")
    text = re.sub(r"<[^>]+>", "", text)
    normalized = html.unescape(text).strip() or "无"
    if len(normalized) > MAX_VALUE_LENGTH:
        return f"{normalized[:MAX_VALUE_LENGTH].rstrip()}…"
    return normalized


def _meaningful_changes(item: dict[str, Any]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for change in item.get("changes", []):
        key = change["key"]
        section = change["section"]
        label = change.get("labelKey", "")
        keep = (
            section in {"profile", "forte", "chains", "refinement"}
            and label in {"name", "description", "simpleDescription"}
        ) or (section == "stats" and key.startswith("stats.90.")) or (
            section == "skills"
            and (
                label in {"description", "simpleDescription"}
                or (".level.10.row." in key and key.endswith(".value"))
            )
        )
        if not keep:
            continue
        before = _plain_text(change.get("before"))
        after = _plain_text(change.get("after"))
        signature = (change.get("context", ""), before, after)
        if before == after or signature in seen:
            continue
        seen.add(signature)
        selected.append(change)
    return selected


def _change_title(change: dict[str, Any]) -> str:
    context = change.get("context")
    label = LABEL_NAMES.get(change.get("labelKey", ""), change.get("labelKey", "变动"))
    return f"{context} · {label}" if context else label


def _entity_name(item: dict[str, Any]) -> str:
    return "角色" if item["entity"] == "character" else "武器"


DPI = 144


async def _render(body: str) -> bytes:
    """渲染 HTML。

    pytakumi 的 max_width 是设备像素，dpi>96 时 CSS 布局宽 = max_width/(dpi/96)，
    必须同时传 root_max_width=CSS 宽度，否则右侧内容被裁切。
    旧版核心没有 root_max_width 参数，回退 dpi=96（dpr=1 不存在该问题）。
    """
    try:
        return await render_html_to_bytes(
            page(body),
            max_width=WIDTH * DPI // 96,
            dpi=DPI,
            root_max_width=WIDTH,
            lang="zh",
            font_name="Noto Sans SC",
        )
    except TypeError:
        return await render_html_to_bytes(
            page(body), max_width=WIDTH, dpi=96, lang="zh", font_name="Noto Sans SC"
        )


async def render_overview(versions: list[str], items: list[dict[str, Any]]) -> bytes:
    cards = []
    for item in items:
        stage_text = []
        for index, stage in enumerate(item["stages"]):
            count = len(_meaningful_changes(stage)) if stage else 0
            result = str(count) if count else ("更新" if stage else "—")
            stage_text.append(f"V{index + 1}→V{index + 2}: <b>{result}</b>")
        cards.append(
            overview_card(item["name"], _entity_name(item), item.get("rarity"), stage_text)
        )

    body = (
        header("鸣潮体验服差异", versions)
        + '<div class="section-title">变动总览</div>'
        + "".join(cards)
        + footer("发送 wwng 名称 查看详情 · Data: nanoka.cc")
    )
    return await _render(body)


async def render_detail(versions: list[str], item: dict[str, Any]) -> bytes:
    parts = [
        header(item["name"], versions),
        f'<div class="sub">{_entity_name(item)} · ID {html.escape(str(item["id"]))}</div>',
    ]

    stage_blocks = []
    for stage_index, stage in enumerate(item["stages"]):
        changes = _meaningful_changes(stage) if stage else []
        if not changes:
            inner = '<div class="empty">此阶段无可读变动～</div>'
        else:
            grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
            for change in changes[:MAX_CHANGES_PER_STAGE]:
                grouped[change["section"]].append(change)
            blocks = []
            for section, section_changes in grouped.items():
                blocks.append(group_title(SECTION_NAMES.get(section, section)))
                blocks.extend(
                    render_change(
                        _change_title(change),
                        _plain_text(change.get("before")),
                        _plain_text(change.get("after")),
                    )
                    for change in section_changes
                )
            hidden_count = len(changes) - MAX_CHANGES_PER_STAGE
            if hidden_count > 0:
                blocks.append(
                    f'<div class="folded">另有 {hidden_count} 项次要变动已折叠</div>'
                )
            inner = "".join(blocks)
        stage_blocks.append(stage_block(stage_index, versions, inner))
    parts.append(f'<div class="stages">{"".join(stage_blocks)}</div>')

    parts.append(footer("粉色为旧值 · 绿色为新值 · 高亮处即改动内容 · Data: nanoka.cc"))
    return await _render("".join(parts))
