"""Compact PIHC3 inventory-item definition and generated helper sources."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from itertools import pairwise

from heavenbase.utils import loads_json
from paradev.build import LocalizationEntry
from paradev.pdx import PDXBlock

INVENTORY_ITEM_DEFINITION_CONTRACT = "pihc3.inventory-item.definition.v1"
INVENTORY_ITEM_DEFINITION_PATH = "item.json"
STANDARD_HELPER_QUANTITIES = (
    *range(1, 101),
    *range(150, 3001, 50),
    9999,
    20000,
    50000,
    99999,
)
STANDARD_HELPER_QUANTITIES_TEXT = "1-100, 150-3000/50, 9999, 20000, 50000, 99999"
_HELPER_QUANTITY_TOKEN = re.compile(
    r"^(?P<start>[1-9][0-9]*)(?:-(?P<end>[1-9][0-9]*)(?:/(?P<step>[1-9][0-9]*))?)?$"
)
_MAX_HELPER_QUANTITY = 99999
_MAX_HELPER_QUANTITIES = 512
_FULL_LOCALIZATION_TEMPLATES = {
    "l_english": {
        "gain": "Gain Item §Y{title}§! ×§Y{count}§!",
        "spend": "Spend Item §Y{title}§! ×§Y{count}§!",
        "own": "Own at least §Y{count}§! Item §Y{title}§!",
        "have": "Own Item §Y{title}§!",
        "not_met": "Require Item §Y{title}§! but we don’t have it yet",
    },
    "l_simp_chinese": {
        "gain": "获得物品 §Y{title}§! ×§Y{count}§!",
        "spend": "消耗物品 §Y{title}§! ×§Y{count}§!",
        "own": "拥有不少于 §Y{count}§! 个物品 §Y{title}§!",
        "have": "拥有物品 §Y{title}§!",
        "not_met": "需要拥有物品 §Y{title}§!，但我们还尚未取得",
    },
}
_RUSSIAN_BASE_LOCALIZATION_TEMPLATES = {
    "have": "Own item {title}",
    "not_met": "Requires item {title}",
}


@dataclass(frozen=True, slots=True)
class InventoryItemDefinition:
    """One compact, validated inventory-item helper declaration."""

    helper_quantities: tuple[int, ...]
    helper_quantities_text: str


def load_inventory_item_definition(
    text: str,
    *,
    label: str,
) -> InventoryItemDefinition:
    """Parse one compact JSON item definition."""

    try:
        value = loads_json(text, restore=False)
    except Exception as error:
        raise ValueError(
            f"Inventory item definition is invalid JSON: {label}: {error}"
        ) from error
    if not isinstance(value, Mapping):
        raise TypeError(f"Inventory item definition must be a JSON object: {label}")
    unknown = sorted(str(key) for key in value if key != "helper_quantities")
    if unknown:
        raise ValueError(
            f"Inventory item definition has unknown fields {', '.join(unknown)}: {label}"
        )
    quantity_text = value.get("helper_quantities")
    if not isinstance(quantity_text, str) or not quantity_text.strip():
        raise ValueError(
            f"Inventory item helper_quantities must be a non-empty range string: {label}"
        )
    return InventoryItemDefinition(
        helper_quantities=parse_helper_quantities(quantity_text),
        helper_quantities_text=quantity_text.strip(),
    )


def parse_helper_quantities(value: str) -> tuple[int, ...]:
    """Expand a concise quantity/range string into a bounded ordered tuple."""

    quantities: list[int] = []
    for raw_token in value.split(","):
        token = raw_token.strip()
        match = _HELPER_QUANTITY_TOKEN.fullmatch(token)
        if match is None:
            raise ValueError(
                "Inventory item helper_quantities entries must be positive integers, "
                "inclusive ranges such as 1-10, or stepped ranges such as 100-1000/50."
            )
        start = int(match.group("start"))
        end = int(match.group("end") or start)
        step = int(match.group("step") or 1)
        if end < start:
            raise ValueError(
                f"Inventory item helper quantity range {token!r} must end at or after its start."
            )
        if max(start, end) > _MAX_HELPER_QUANTITY:
            raise ValueError(
                f"Inventory item helper quantities must not exceed {_MAX_HELPER_QUANTITY}."
            )
        quantities.extend(range(start, end + 1, step))
        if len(quantities) > _MAX_HELPER_QUANTITIES:
            raise ValueError(
                f"Inventory item definitions may generate at most {_MAX_HELPER_QUANTITIES} quantities."
            )
    if not quantities:
        raise ValueError(
            "Inventory item helper_quantities must declare at least one quantity."
        )
    if any(current <= previous for previous, current in pairwise(quantities)):
        raise ValueError(
            "Inventory item helper quantities must be unique and strictly increasing."
        )
    return tuple(quantities)


def inventory_item_definition_source_form(
    definition: InventoryItemDefinition,
) -> dict[str, object]:
    """Project the compact definition into one generic JSON scalar control."""

    return {
        "contract": INVENTORY_ITEM_DEFINITION_CONTRACT,
        "label": {
            "default": "Inventory item",
            "zh": "库存物品",
        },
        "description": {
            "default": (
                "Edit the quantities for which ParaDev generates add, remove, and "
                "ownership helpers. Definitions, tooltips, and translations are generated."
            ),
            "zh": "编辑需要生成增加、移除与持有辅助脚本的数量；定义、提示与翻译由 ParaDev 生成。",
        },
        "sections": [
            {
                "id": "inventory-item-definition",
                "label": {
                    "default": "Generated helpers",
                    "zh": "生成的辅助脚本",
                },
                "controls": [
                    {
                        "id": "helper_quantities",
                        "label": {
                            "default": "Helper quantities",
                            "zh": "辅助脚本数量",
                        },
                        "description": {
                            "default": (
                                "Comma-separated numbers or inclusive ranges. Use /step for "
                                "a stepped range, for example 1-100, 150-3000/50."
                            ),
                            "zh": "使用逗号分隔数字或闭区间；用 /步长 表示步进区间，例如 1-100, 150-3000/50。",
                        },
                        "description_source": "declared",
                        "control": "text",
                        "value": definition.helper_quantities_text,
                        "placeholder": STANDARD_HELPER_QUANTITIES_TEXT,
                        "patch": {
                            "op": "replace-json-scalar",
                            "path": ["helper_quantities"],
                        },
                    }
                ],
            }
        ],
    }


def inventory_effects_block(
    object_id: str,
    quantities: Sequence[int],
) -> PDXBlock:
    """Generate canonical add/remove helpers for one inventory item."""

    rows: list[str] = []
    for count in quantities:
        rows.append(f"""ADD_INVENTORY_ITEM_{object_id}_{count} = {{
 custom_effect_tooltip = CUSTOM_GAIN_INVENTORY_ITEM_{object_id}_{count}
 add_to_variable = {{ VAR_INVENTORY_ITEM_{object_id} = {count} }}
 INVENTORY_RELOAD_ONLY_WHEN_OPEN = yes
}}
DEL_INVENTORY_ITEM_{object_id}_{count} = {{
 custom_effect_tooltip = CUSTOM_SPEND_INVENTORY_ITEM_{object_id}_{count}
 add_to_variable = {{ VAR_INVENTORY_ITEM_{object_id} = -{count} }}
 clamp_variable = {{ var = VAR_INVENTORY_ITEM_{object_id} min = 0 }}
 INVENTORY_RELOAD_ONLY_WHEN_OPEN = yes
}}""")
    return PDXBlock.from_str("\n".join(rows) + "\n")


def inventory_triggers_block(
    object_id: str,
    quantities: Sequence[int],
) -> PDXBlock:
    """Generate canonical ownership helpers for one inventory item."""

    rows = [f"""TRIGGER_HAVE_INVENTORY_ITEM_{object_id} = {{
 custom_trigger_tooltip = {{
  tooltip = HAVE_INVENTORY_ITEM_{object_id}
  check_variable = {{ var = VAR_INVENTORY_ITEM_{object_id} value = 1 compare = greater_than_or_equals }}
 }}
}}
TRIGGER_HAVE_INVENTORY_ITEM_{object_id}_IF = {{
 if = {{
  limit = {{ NOT = {{ check_variable = {{ var = VAR_INVENTORY_ITEM_{object_id} value = 1 compare = greater_than_or_equals }} }} }}
  custom_trigger_tooltip = {{ tooltip = HAVE_INVENTORY_ITEM_{object_id}_NOT_MET always = no }}
 }}
}}"""]
    rows.extend(f"""TRIGGER_HAVE_INVENTORY_ITEM_{object_id}_{count} = {{
 custom_trigger_tooltip = {{
  tooltip = CUSTOM_OWN_INVENTORY_ITEM_{object_id}_{count}
  check_variable = {{ var = VAR_INVENTORY_ITEM_{object_id} value = {count} compare = greater_than_or_equals }}
 }}
}}""" for count in quantities)
    return PDXBlock.from_str("\n".join(rows) + "\n")


def generated_inventory_localization_values(
    object_id: str,
    quantities: Sequence[int],
    authored_entries: Sequence[LocalizationEntry],
) -> dict[tuple[str, str], str]:
    """Return deterministic helper localization derived from item titles."""

    authored = {(entry.language, entry.key): entry.text for entry in authored_entries}
    languages = sorted({entry.language for entry in authored_entries})
    generated: dict[tuple[str, str], str] = {}
    for language in languages:
        title_key = f"INVENTORY_ITEM_{object_id}"
        title = authored.get((language, title_key))
        if not isinstance(title, str) or not title.strip():
            raise ValueError(
                f"Inventory item {object_id!r} language {language!r} must define {title_key}."
            )
        generated[(language, f"INVENTORY_ITEM_{object_id}_COUNT")] = (
            f"[?VAR_INVENTORY_ITEM_{object_id}|Y0]"
        )
        if language == "l_simp_chinese":
            templates = _FULL_LOCALIZATION_TEMPLATES[language]
            include_quantity_tooltips = True
        elif language == "l_russian":
            templates = _RUSSIAN_BASE_LOCALIZATION_TEMPLATES
            include_quantity_tooltips = False
        else:
            templates = _FULL_LOCALIZATION_TEMPLATES["l_english"]
            include_quantity_tooltips = True
        generated[(language, f"HAVE_INVENTORY_ITEM_{object_id}")] = templates[
            "have"
        ].format(title=title)
        generated[(language, f"HAVE_INVENTORY_ITEM_{object_id}_NOT_MET")] = templates[
            "not_met"
        ].format(title=title)
        if not include_quantity_tooltips:
            continue
        for count in quantities:
            generated[(language, f"CUSTOM_GAIN_INVENTORY_ITEM_{object_id}_{count}")] = (
                templates["gain"].format(title=title, count=count)
            )
            generated[
                (language, f"CUSTOM_SPEND_INVENTORY_ITEM_{object_id}_{count}")
            ] = templates["spend"].format(title=title, count=count)
            generated[(language, f"CUSTOM_OWN_INVENTORY_ITEM_{object_id}_{count}")] = (
                templates["own"].format(title=title, count=count)
            )
    return generated


def generated_inventory_localization_entries(
    object_id: str,
    quantities: Sequence[int],
    authored_entries: Sequence[LocalizationEntry],
    *,
    source_path: str = INVENTORY_ITEM_DEFINITION_PATH,
    module_id: str | None = None,
) -> tuple[LocalizationEntry, ...]:
    """Return generated helper localizations as compiler payload entries."""

    values = generated_inventory_localization_values(
        object_id,
        quantities,
        authored_entries,
    )
    return tuple(
        LocalizationEntry(
            key=key,
            language=language,
            text=text,
            source_path=source_path,
            module_id=module_id,
        )
        for (language, key), text in sorted(values.items())
    )


def is_generated_inventory_localization_key(object_id: str, key: str) -> bool:
    """Return whether the compiler, rather than the author, owns one key."""

    fixed = {
        f"INVENTORY_ITEM_{object_id}_COUNT",
        f"HAVE_INVENTORY_ITEM_{object_id}",
        f"HAVE_INVENTORY_ITEM_{object_id}_NOT_MET",
    }
    if key in fixed:
        return True
    return any(
        key.startswith(prefix) and key.removeprefix(prefix).isdigit()
        for prefix in (
            f"CUSTOM_GAIN_INVENTORY_ITEM_{object_id}_",
            f"CUSTOM_SPEND_INVENTORY_ITEM_{object_id}_",
            f"CUSTOM_OWN_INVENTORY_ITEM_{object_id}_",
        )
    )


__all__ = [
    "INVENTORY_ITEM_DEFINITION_CONTRACT",
    "INVENTORY_ITEM_DEFINITION_PATH",
    "STANDARD_HELPER_QUANTITIES",
    "STANDARD_HELPER_QUANTITIES_TEXT",
    "InventoryItemDefinition",
    "generated_inventory_localization_entries",
    "generated_inventory_localization_values",
    "inventory_effects_block",
    "inventory_item_definition_source_form",
    "inventory_triggers_block",
    "is_generated_inventory_localization_key",
    "load_inventory_item_definition",
    "parse_helper_quantities",
]
