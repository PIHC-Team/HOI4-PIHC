"""PIHC3 division Entity and compiler."""

from __future__ import annotations

import heavenbase as hb

from paradev.build import SimpleSourceFamily, Slot

_SOURCE_FORM_FIELD_HINTS = {
    "name": {
        "label": {"default": "Division name", "zh": "师名称"},
        "description": {
            "default": "Displayed template, deployed-division, fleet, or naming-group title at this source location.",
            "zh": "此处显示的编制、已部署部队、舰队或命名组名称。",
        },
    },
    "location": {
        "label": {"default": "Deployment state", "zh": "部署地区"},
        "description": {
            "default": "Numeric state identifier where this division starts the scenario.",
            "zh": "此部队在剧本开始时所在的地区数字 ID。",
        },
    },
    "division_names_group": {
        "label": {"default": "Names group", "zh": "部队命名组"},
        "description": {
            "default": "Naming-group identifier used to generate division names.",
            "zh": "用于生成部队名称的命名组标识。",
        },
    },
    "priority": {
        "label": {"default": "Template priority", "zh": "编制优先级"},
        "description": {
            "default": "Relative priority used when the game chooses among division templates.",
            "zh": "游戏在多个部队编制之间选择时使用的相对优先级。",
        },
    },
    "fallback_name": {
        "label": {"default": "Fallback name", "zh": "备用名称格式"},
        "description": {
            "default": "Printf-style name used after the explicit division-name list is exhausted.",
            "zh": "显式部队名称用尽后采用的 printf 风格名称格式。",
        },
    },
    "regiments": {
        "label": {"default": "Line battalions", "zh": "战斗营编制"},
        "description": {
            "default": "Battalion types and grid positions in the division's line formation.",
            "zh": "部队战斗营的类型及其编制网格位置。",
        },
        "control": "block-text",
    },
    "support": {
        "label": {"default": "Support companies", "zh": "支援连编制"},
        "description": {
            "default": "Support-company types and grid positions assigned to this template.",
            "zh": "分配给此编制的支援连类型及网格位置。",
        },
        "control": "block-text",
    },
    "for_countries": {
        "label": {"default": "Countries", "zh": "适用国家"},
        "description": {
            "default": "Country tags allowed to use this division naming group.",
            "zh": "可以使用此部队命名组的国家标签。",
        },
        "control": "block-text",
    },
    "division_types": {
        "label": {"default": "Division types", "zh": "部队类型"},
        "description": {
            "default": "Battalion types for which this naming group is eligible.",
            "zh": "此命名组可用于的营种类型。",
        },
        "control": "block-text",
    },
    "can_use": {
        "label": {"default": "Naming availability", "zh": "命名组可用条件"},
        "description": {
            "default": "Conditions controlling whether this naming group may be selected.",
            "zh": "控制此命名组是否可以被选择的条件。",
        },
        "control": "block-text",
    },
}


class PIHC3Division(hb.Entity):
    """One PIHC3 division history and naming resource set."""

    identifier = "pihc3-division"
    title = hb.field(hb.ShortText).default("")
    family = "division"
    resource_slots = (
        Slot(
            "history",
            r"^history/units/.*\.txt$",
            required=True,
            many=True,
            regex=True,
            kind="pdx",
        ),
        Slot(
            "names",
            r"^common/units/names_divisions/.*\.txt$",
            many=True,
            regex=True,
            kind="pdx",
        ),
    )
    compilation_hooks = ("normalize", "check", "emit")
    source_form_field_hints = _SOURCE_FORM_FIELD_HINTS

    @classmethod
    def build_family(cls) -> PIHC3DivisionFamily:
        """Return the division compiler."""

        return PIHC3DivisionFamily()


class PIHC3DivisionFamily(SimpleSourceFamily):
    """Compile division resources to their exact authored game paths."""

    replaces_registered_family = True
    source_form_field_hints = _SOURCE_FORM_FIELD_HINTS

    def __init__(self) -> None:
        super().__init__(
            family=PIHC3Division.family,
            pdx_path_template="{source_path}",
            source_slots=PIHC3Division.resource_slots,
        )


def build_family() -> PIHC3DivisionFamily:
    """HeavenBase Registry target for the division compiler."""

    return PIHC3Division.build_family()
