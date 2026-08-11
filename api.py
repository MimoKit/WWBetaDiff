import json
import asyncio
from typing import Any
from pathlib import Path
from urllib.parse import quote

import httpx
import aiofiles

from gsuid_core.data_store import get_res_path

STATIC_ROOT = "https://static.nanoka.cc"
MANIFEST_URL = f"{STATIC_ROOT}/manifest.json"
CACHE_PATH = get_res_path(["WWBetaDiff", "cache"])


async def _read_cache(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    async with aiofiles.open(path, encoding="utf-8") as cache_file:
        return json.loads(await cache_file.read())


async def _write_cache(path: Path, data: dict[str, Any]) -> None:
    async with aiofiles.open(path, "w", encoding="utf-8") as cache_file:
        await cache_file.write(json.dumps(data, ensure_ascii=False))


async def _fetch_json(url: str, cache_name: str) -> dict[str, Any]:
    cache_file = CACHE_PATH / cache_name
    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
        data = response.json()
        await _write_cache(cache_file, data)
        return data
    except (httpx.HTTPError, json.JSONDecodeError):
        cached = await _read_cache(cache_file)
        if cached is None:
            raise
        return cached


async def get_beta_diffs() -> tuple[list[str], list[dict[str, Any]]]:
    manifest = await _fetch_json(MANIFEST_URL, "manifest.json")
    versions = manifest["ww"]["available"][-3:]
    if len(versions) < 3:
        raise ValueError("体验服版本快照不足 3 个")

    urls = []
    for old_version, new_version in zip(versions, versions[1:]):
        encoded_old = quote(old_version, safe="")
        encoded_new = quote(new_version, safe="")
        url = (
            f"{STATIC_ROOT}/ww/{encoded_new}/diff/"
            f"from-{encoded_old}/zh.json"
        )
        cache_name = f"diff_{old_version}_{new_version}.json".replace("/", "_")
        urls.append(_fetch_json(url, cache_name))

    return versions, list(await asyncio.gather(*urls))


def merge_items(diffs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for stage, diff_data in enumerate(diffs):
        for item in diff_data["items"]:
            item_id = str(item["id"])
            if item_id not in merged:
                merged[item_id] = {
                    "id": item_id,
                    "entity": item["entity"],
                    "name": item["name"],
                    "rarity": item.get("rarity", 5),
                    "stages": [None, None],
                }
            merged[item_id]["name"] = item.get("afterName") or item["name"]
            merged[item_id]["stages"][stage] = item
    return sorted(
        merged.values(),
        key=lambda item: (item["entity"] != "character", item["name"]),
    )


def find_item(items: list[dict[str, Any]], query: str) -> dict[str, Any] | None:
    normalized = query.strip().lower().replace(" ", "")
    exact = [
        item
        for item in items
        if normalized in {item["id"].lower(), item["name"].lower().replace(" ", "")}
    ]
    if exact:
        return exact[0]
    partial = [
        item
        for item in items
        if normalized in item["name"].lower().replace(" ", "")
    ]
    return partial[0] if len(partial) == 1 else None
