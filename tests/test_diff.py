from gsuid_core.plugins.WWBetaDiff.api import find_item, merge_items
from gsuid_core.plugins.WWBetaDiff.render import _plain_text, _meaningful_changes


def test_merge_items_tracks_both_stages() -> None:
    diffs = [
        {"items": [{"id": "1", "entity": "character", "name": "甲", "changes": []}]},
        {"items": [{"id": "1", "entity": "character", "name": "乙", "changes": []}]},
    ]
    items = merge_items(diffs)
    assert items[0]["name"] == "乙"
    assert items[0]["stages"][0] is not None
    assert items[0]["stages"][1] is not None


def test_find_item_supports_name_and_id() -> None:
    items = [{"id": "1212", "name": "景燃"}]
    assert find_item(items, "景燃") == items[0]
    assert find_item(items, "1212") == items[0]


def test_meaningful_changes_filters_raw_damage_rows() -> None:
    item = {
        "changes": [
            {
                "section": "skills",
                "key": "skill.1.level.10.row.倍率.value",
                "labelKey": "value",
                "before": "10%",
                "after": "20%",
            },
            {
                "section": "skills",
                "key": "skill.1.level.9.damage.1.rate",
                "labelKey": "damageRate",
                "before": "10%",
                "after": "20%",
            },
        ]
    }
    changes = _meaningful_changes(item)
    assert len(changes) == 1
    assert changes[0]["key"].endswith(".value")


def test_plain_text_removes_markup() -> None:
    assert _plain_text("<strong>测试</strong><br />下一行") == "测试\n下一行"
