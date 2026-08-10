"""PIHC3 compiler overlay for the built-in modifier family."""

from __future__ import annotations

from typing import ClassVar

from paradev.build import CollectionSourceFamily, Slot

MODIFIER_SOURCE_FORM_FIELD_HINTS = {
    "$root": {
        "label": {"default": "Modifier body", "zh": "修正内容"},
        "description": {
            "default": "All modifier values owned by this independently editable modifier record.",
            "zh": "此独立可编辑修正记录所拥有的全部修正值。",
        },
        "placeholder": {
            "default": "political_power_factor = 0.05",
            "zh": "political_power_factor = 0.05",
        },
        "control": "block-text",
    }
}

MODIFIER_RESOURCE_SLOTS = (
    Slot("def", "def.txt", required=True, kind="pdx"),
    Slot("loc", "**/*.loc", many=True, kind="loc"),
    Slot(
        "assets",
        r"^gfx/interface/modifiers/.+\.dds$",
        many=True,
        regex=True,
        kind="copy",
        authoring_path="gfx/interface/modifiers/{filename}",
    ),
    Slot(
        "assets",
        r"^interface/modifiers/.+\.gfx$",
        many=True,
        regex=True,
        kind="copy",
        authoring_path="interface/modifiers/{filename}",
    ),
)


class PIHC3ModifierFamily(CollectionSourceFamily):
    """Compile modifiers standalone or inside modifier collections."""

    replaces_registered_family = True
    source_form_field_hints: ClassVar[dict[str, dict[str, object]]] = MODIFIER_SOURCE_FORM_FIELD_HINTS

    def __init__(self) -> None:
        super().__init__(
            family="modifier",
            pdx_path_template="common/modifiers/{collection_id}.txt",
            module_pdx_path_template="common/modifiers/{object_id}.txt",
            loc_path_template=("localisation/{language_folder}/{object_id}_{language}.yml"),
            copy_path_template="{source_path}",
            source_slots=MODIFIER_RESOURCE_SLOTS,
        )


def build_family() -> PIHC3ModifierFamily:
    """Return the PIHC3 overlay for the built-in modifier family."""

    return PIHC3ModifierFamily()
