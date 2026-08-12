"""HTML 拼装层：加载 templates/ 下的模板与样式，填占位符。数据过滤逻辑在 render.py。"""

import html
import base64
import difflib
from typing import Any
from pathlib import Path
from functools import lru_cache
from string import Template

WIDTH = 1080

ASSET_DIR = Path(__file__).parent
FONT_DIR = ASSET_DIR / "fonts"
FONT_FILES = {
    400: FONT_DIR / "NotoSansSC-Regular.ttf",
    700: FONT_DIR / "NotoSansSC-Bold.ttf",
}
FONT_FAMILY = "Noto Sans SC"
TEMPLATE_DIR = ASSET_DIR / "templates"


def register_fonts() -> None:
    """把插件内置字体注册到 GsCore 的共享 pytakumi 渲染器。

    pytakumi 只使用显式注册的字体——系统字体、fontconfig、CSS data URI
    统统不生效，所以必须在渲染器上 register_font。旧版核心(htmlkit)下
    静默跳过，走字体兜底。
    """
    try:
        from gsuid_core.utils import html_render as core_html_render

        ensure_renderer = getattr(core_html_render, "_ensure_renderer", None)
        if ensure_renderer is None:
            return
        renderer = ensure_renderer()
        for weight, font_file in FONT_FILES.items():
            if font_file.exists():
                renderer.register_font(
                    font_file.read_bytes(), name=FONT_FAMILY, weight=float(weight)
                )
    except Exception:  # noqa: BLE001 - 字体注册失败不应影响插件加载
        pass


register_fonts()


@lru_cache(maxsize=1)
def _font_faces() -> str:
    blocks = []
    for weight, font_file in FONT_FILES.items():
        if not font_file.exists():
            continue
        encoded = base64.b64encode(font_file.read_bytes()).decode("ascii")
        blocks.append(
            "@font-face {\n"
            f"    font-family: '{FONT_FAMILY}';\n"
            f"    font-weight: {weight};\n"
            f"    src: url(data:font/ttf;base64,{encoded}) format('truetype');\n"
            "}"
        )
    return "\n".join(blocks)


@lru_cache(maxsize=1)
def _style() -> str:
    return (
        (TEMPLATE_DIR / "style.css")
        .read_text(encoding="utf-8")
        .replace("__FONT_FACES__", _font_faces())
        .replace("__WIDTH__", str(WIDTH))
    )


@lru_cache(maxsize=None)
def _tpl(name: str) -> Template:
    return Template((TEMPLATE_DIR / name).read_text(encoding="utf-8"))


def page(body: str) -> str:
    return _tpl("page.html").substitute(style=_style(), body=body)


def header(title: str, versions: list[str]) -> str:
    chips = "".join(
        f"<span>V{index + 1} {html.escape(version)}</span>"
        for index, version in enumerate(versions)
    )
    return _tpl("header.html").substitute(title=html.escape(title), chips=chips)


def _diff_marked(before: str, after: str) -> tuple[str, str]:
    """逐字符对比，给真正改动的部分加 <mark> 高亮，一眼看出改了哪里。"""
    before_html: list[str] = []
    after_html: list[str] = []
    matcher = difflib.SequenceMatcher(None, before, after, autojunk=False)
    for tag, b1, b2, a1, a2 in matcher.get_opcodes():
        before_part = html.escape(before[b1:b2])
        after_part = html.escape(after[a1:a2])
        if tag == "equal":
            before_html.append(before_part)
            after_html.append(after_part)
        else:
            if before_part:
                before_html.append(f"<mark>{before_part}</mark>")
            if after_part:
                after_html.append(f"<mark>{after_part}</mark>")
    return "".join(before_html), "".join(after_html)


def render_change(title: str, before: str, after: str) -> str:
    before_html, after_html = _diff_marked(before, after)
    return _tpl("change.html").substitute(
        title=html.escape(title), before=before_html, after=after_html
    )


def overview_card(name: str, entity: str, rarity: Any, stage_text: list[str]) -> str:
    return _tpl("overview_card.html").substitute(
        name=html.escape(name),
        entity=entity,
        stars="★" * int(rarity or 5),
        stages="　".join(stage_text),
    )


def stage_block(stage_index: int, versions: list[str], inner: str) -> str:
    version_range = html.escape(
        f"{versions[stage_index]} → {versions[stage_index + 1]}"
    )
    return _tpl("stage_block.html").substitute(
        from_index=stage_index + 1,
        to_index=stage_index + 2,
        version_range=version_range,
        inner=inner,
    )


def group_title(name: str) -> str:
    return _tpl("group_title.html").substitute(name=html.escape(name))


def footer(text: str) -> str:
    return _tpl("footer.html").substitute(text=html.escape(text))
