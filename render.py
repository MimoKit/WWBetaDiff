import re
import html
from typing import Any
from collections import defaultdict

from PIL import Image, ImageDraw

from gsuid_core.utils.fonts.fonts import core_font
from gsuid_core.utils.image.convert import convert_img

WIDTH = 1000
MARGIN = 44
BG = "#0d1019"
PANEL = "#151925"
PANEL_ALT = "#11151f"
TEXT = "#e8ebf4"
MUTED = "#9299aa"
ACCENT = "#b68cff"
GREEN = "#86d89b"
RED = "#ef91a5"
ORANGE = "#ffad68"
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


def _wrap(draw: ImageDraw.ImageDraw, text: str, font_size: int, width: int) -> list[str]:
    font = core_font(font_size)
    lines: list[str] = []
    for paragraph in text.splitlines() or [""]:
        current = ""
        for char in paragraph:
            candidate = current + char
            if draw.textlength(candidate, font=font) <= width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = char
        lines.append(current)
    return lines or [""]


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


def _measure_change(draw: ImageDraw.ImageDraw, change: dict[str, Any], col_width: int) -> int:
    title_h = 31
    body_width = col_width - 28
    before_lines = _wrap(draw, _plain_text(change.get("before")), 20, body_width)
    after_lines = _wrap(draw, _plain_text(change.get("after")), 20, body_width)
    return title_h + (len(before_lines) + len(after_lines)) * 29 + 29


async def render_overview(versions: list[str], items: list[dict[str, Any]]) -> bytes:
    height = 255 + len(items) * 112
    image = Image.new("RGB", (WIDTH, height), BG)
    draw = ImageDraw.Draw(image)
    _draw_header(draw, "鸣潮体验服差异", versions)
    y = 190
    draw.text((MARGIN, y), "变动总览", font=core_font(30), fill=ACCENT)
    y += 54
    for item in items:
        x2 = WIDTH - MARGIN
        draw.rounded_rectangle((MARGIN, y, x2, y + 88), 10, fill=PANEL)
        entity = "角色" if item["entity"] == "character" else "武器"
        stars = "★" * int(item.get("rarity", 5))
        draw.text((MARGIN + 22, y + 15), item["name"], font=core_font(28), fill=TEXT)
        draw.text((MARGIN + 22, y + 52), f"{entity}  {stars}", font=core_font(18), fill=ORANGE)
        stage_text = []
        for index, stage in enumerate(item["stages"]):
            count = len(_meaningful_changes(stage)) if stage else 0
            result = str(count) if count else ("更新" if stage else "—")
            stage_text.append(f"V{index + 1}→V{index + 2}: {result}")
        right = "   ".join(stage_text)
        right_width = draw.textlength(right, font=core_font(20))
        draw.text((x2 - right_width - 22, y + 34), right, font=core_font(20), fill=MUTED)
        y += 112
    draw.text(
        (MARGIN, height - 38),
        "发送 ww diff 名称 查看详情  ·  Data: nanoka.cc",
        font=core_font(17),
        fill=MUTED,
    )
    return await convert_img(image)


async def render_detail(
    versions: list[str],
    item: dict[str, Any],
) -> bytes:
    stages = []
    for index, stage in enumerate(item["stages"]):
        changes = _meaningful_changes(stage) if stage else []
        stages.append((index, changes))

    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    col_width = (WIDTH - MARGIN * 2 - 18) // 2
    content_height = 0
    for _, changes in stages:
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for change in changes[:MAX_CHANGES_PER_STAGE]:
            grouped[change["section"]].append(change)
        stage_height = 68
        for section_changes in grouped.values():
            stage_height += 48
            stage_height += sum(_measure_change(probe, change, col_width) for change in section_changes)
        content_height = max(content_height, stage_height)

    height = max(520, 245 + content_height + 70)
    image = Image.new("RGB", (WIDTH, height), BG)
    draw = ImageDraw.Draw(image)
    _draw_header(draw, item["name"], versions)
    entity = "角色" if item["entity"] == "character" else "武器"
    draw.text((MARGIN, 151), f"{entity} · ID {item['id']}", font=core_font(21), fill=MUTED)

    for column, (stage_index, changes) in enumerate(stages):
        x = MARGIN + column * (col_width + 18)
        y = 205
        draw.rounded_rectangle((x, y, x + col_width, y + content_height), 10, fill=PANEL_ALT)
        draw.text(
            (x + 18, y + 17),
            f"V{stage_index + 1} → V{stage_index + 2}",
            font=core_font(25),
            fill=ACCENT,
        )
        draw.text(
            (x + col_width - 190, y + 22),
            f"{versions[stage_index]} → {versions[stage_index + 1]}",
            font=core_font(15),
            fill=MUTED,
        )
        y += 64
        if not changes:
            draw.text((x + 18, y), "此阶段无可读变动", font=core_font(21), fill=MUTED)
            continue

        grouped = defaultdict(list)
        for change in changes[:MAX_CHANGES_PER_STAGE]:
            grouped[change["section"]].append(change)
        for section, section_changes in grouped.items():
            draw.text(
                (x + 18, y),
                SECTION_NAMES.get(section, section),
                font=core_font(23),
                fill=ORANGE,
            )
            y += 42
            for change in section_changes:
                block_h = _measure_change(draw, change, col_width)
                draw.rounded_rectangle(
                    (x + 12, y, x + col_width - 12, y + block_h - 10),
                    7,
                    fill=PANEL,
                )
                draw.text((x + 24, y + 10), _change_title(change), font=core_font(19), fill=TEXT)
                body_y = y + 41
                body_width = col_width - 48
                before_lines = _wrap(draw, _plain_text(change.get("before")), 20, body_width)
                after_lines = _wrap(draw, _plain_text(change.get("after")), 20, body_width)
                for line_index, line in enumerate(before_lines):
                    draw.text((x + 24, body_y + line_index * 29), line, font=core_font(20), fill=RED)
                after_y = body_y + len(before_lines) * 29 + 5
                for line_index, line in enumerate(after_lines):
                    draw.text((x + 24, after_y + line_index * 29), line, font=core_font(20), fill=GREEN)
                y += block_h

        hidden_count = len(changes) - MAX_CHANGES_PER_STAGE
        if hidden_count > 0:
            draw.text(
                (x + 18, y + 4),
                f"另有 {hidden_count} 项次要变动已折叠",
                font=core_font(18),
                fill=MUTED,
            )

    draw.text(
        (MARGIN, height - 38),
        "红色为旧值，绿色为新值  ·  Data: nanoka.cc",
        font=core_font(17),
        fill=MUTED,
    )
    return await convert_img(image)


def _draw_header(draw: ImageDraw.ImageDraw, title: str, versions: list[str]) -> None:
    draw.rectangle((0, 0, WIDTH, 132), fill="#151d32")
    draw.text((MARGIN, 30), title, font=core_font(47), fill=TEXT)
    draw.text(
        (MARGIN, 96),
        f"V1 {versions[0]}   V2 {versions[1]}   V3 {versions[2]}",
        font=core_font(19),
        fill=ACCENT,
    )
