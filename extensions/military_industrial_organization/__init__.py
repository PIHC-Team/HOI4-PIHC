"""PIHC3 military-industrial-organization Entity and compiler."""

from __future__ import annotations

from dataclasses import replace

import heavenbase as hb

from paradev.build import (
    ModuleDiagramProvider,
    SimpleSourceFamily,
    Slot,
)
from paradev.games.hoi4.diagram_providers import MIO_DIAGRAM_PROVIDER

_SOURCE_FORM_FIELD_HINTS = {
    "name": {
        "label": {"default": "Display name key", "zh": "显示名称键"},
        "description": {
            "default": "Localization key shown for this organization, policy, or trait.",
            "zh": "此军工机构、政策或特质所显示的本地化键。",
        },
    },
    "icon": {
        "label": {"default": "Icon sprite", "zh": "图标精灵"},
        "description": {
            "default": "GFX sprite identifier used for this organization, policy, or trait.",
            "zh": "此军工机构、政策或特质使用的 GFX 精灵标识。",
        },
    },
    "include": {
        "label": {"default": "Base organization", "zh": "基础军工机构"},
        "description": {
            "default": "Organization identifier whose definition is inherited here.",
            "zh": "此处继承定义的军工机构标识。",
        },
    },
    "text": {
        "label": {"default": "Tree header key", "zh": "特质树标题键"},
        "description": {
            "default": "Localization key displayed above this part of the MIO trait tree.",
            "zh": "显示在军工机构特质树此区域上方的本地化键。",
        },
    },
    "token": {
        "label": {"default": "Trait token", "zh": "特质标识"},
        "description": {
            "default": "Stable trait identifier used by tree relationships and localization.",
            "zh": "供特质树关系和本地化引用的稳定特质标识。",
        },
    },
    "relative_position_id": {
        "label": {"default": "Position anchor trait", "zh": "位置锚点特质"},
        "description": {
            "default": "Trait token used as the relative-position anchor for this node.",
            "zh": "作为此节点相对位置锚点的特质标识。",
        },
    },
    "x": {
        "label": {"default": "Tree X", "zh": "特质树 X 坐标"},
        "description": {
            "default": "Horizontal tree coordinate, relative to the declared anchor when present.",
            "zh": "特质树水平坐标；存在锚点时为相对于锚点的位置。",
        },
    },
    "y": {
        "label": {"default": "Tree Y", "zh": "特质树 Y 坐标"},
        "description": {
            "default": "Vertical tree coordinate, relative to the declared anchor when present.",
            "zh": "特质树垂直坐标；存在锚点时为相对于锚点的位置。",
        },
    },
    "all_parents": {
        "label": {"default": "Required parent traits", "zh": "必需父特质"},
        "description": {
            "default": "Trait tokens that must all be selected before this trait unlocks.",
            "zh": "解锁此特质前必须全部选中的父特质标识。",
        },
        "control": "block-text",
    },
    "any_parent": {
        "label": {"default": "Alternative parent traits", "zh": "可选父特质"},
        "description": {
            "default": "Trait tokens where selecting any one may unlock this trait.",
            "zh": "选中其中任一项即可解锁此特质的父特质标识。",
        },
        "control": "block-text",
    },
    "allowed": {
        "label": {"default": "Availability conditions", "zh": "可用条件"},
        "description": {
            "default": "PDX conditions controlling which countries or organizations may use this definition.",
            "zh": "控制哪些国家或军工机构可以使用此定义的 PDX 条件。",
        },
        "control": "block-text",
    },
    "visible": {
        "label": {"default": "Visibility conditions", "zh": "显示条件"},
        "description": {
            "default": "PDX conditions controlling whether this organization is shown.",
            "zh": "控制此军工机构是否显示的 PDX 条件。",
        },
        "control": "block-text",
    },
    "equipment_type": {
        "label": {"default": "Equipment types", "zh": "装备类型"},
        "description": {
            "default": "Equipment archetypes this organization can design or produce.",
            "zh": "此军工机构可以设计或生产的装备原型。",
        },
        "control": "block-text",
    },
    "research_categories": {
        "label": {"default": "Research categories", "zh": "研究类别"},
        "description": {
            "default": "Technology categories supported by this organization.",
            "zh": "此军工机构支持的科技类别。",
        },
        "control": "block-text",
    },
    "limit_to_equipment_type": {
        "label": {"default": "Trait equipment limit", "zh": "特质装备限制"},
        "description": {
            "default": "Equipment types to which this trait's bonuses apply.",
            "zh": "此特质加成适用的装备类型。",
        },
        "control": "block-text",
    },
    "mutually_exclusive": {
        "label": {"default": "Mutually exclusive traits", "zh": "互斥特质"},
        "description": {
            "default": "Trait tokens that cannot be selected together with this trait.",
            "zh": "不能与此特质同时选择的特质标识。",
        },
        "control": "block-text",
    },
    "organization_modifier": {
        "label": {"default": "Organization modifiers", "zh": "军工机构修正"},
        "description": {
            "default": "Bonuses applied to the MIO organization itself.",
            "zh": "应用于军工机构本身的加成。",
        },
        "control": "block-text",
    },
    "production_bonus": {
        "label": {"default": "Production bonuses", "zh": "生产加成"},
        "description": {
            "default": "Production-line bonuses granted by this trait or policy.",
            "zh": "此特质或政策提供的生产线加成。",
        },
        "control": "block-text",
    },
    "equipment_bonus": {
        "label": {"default": "Equipment bonuses", "zh": "装备加成"},
        "description": {
            "default": "Equipment-stat bonuses granted by this trait or policy.",
            "zh": "此特质或政策提供的装备属性加成。",
        },
        "control": "block-text",
    },
}


class PIHC3MilitaryIndustrialOrganization(hb.Entity):
    """One PIHC3 MIO definition with an editable trait tree."""

    identifier = "pihc3-military-industrial-organization"
    title = hb.field(hb.ShortText).default("")
    family = "military_industrial_organization"
    resource_slots = (
        Slot(
            "pdx",
            r"^common/military_industrial_organization/.*\.txt$",
            required=True,
            many=True,
            regex=True,
            kind="pdx",
        ),
        Slot(
            "loc",
            "localization/*.loc",
            many=True,
            kind="loc",
        ),
    )
    compilation_hooks = ("normalize", "check", "emit")
    source_form_field_hints = _SOURCE_FORM_FIELD_HINTS

    @classmethod
    def build_family(
        cls,
    ) -> PIHC3MilitaryIndustrialOrganizationFamily:
        """Return the MIO compiler."""

        return PIHC3MilitaryIndustrialOrganizationFamily()


class PIHC3MilitaryIndustrialOrganizationFamily(SimpleSourceFamily):
    """Compile MIO organizations and their trait-tree localization."""

    replaces_registered_family = True
    source_form_field_hints = _SOURCE_FORM_FIELD_HINTS

    def __init__(self) -> None:
        super().__init__(
            family=PIHC3MilitaryIndustrialOrganization.family,
            pdx_path_template="{source_path}",
            loc_path_template=(
                "localisation/{language_folder}/"
                "MILITARY_INDUSTRIAL_ORGANIZATION_"
                "{source_stem}_{language}.yml"
            ),
            source_slots=(PIHC3MilitaryIndustrialOrganization.resource_slots),
        )


def build_family() -> PIHC3MilitaryIndustrialOrganizationFamily:
    """HeavenBase Registry target for the MIO compiler."""

    return PIHC3MilitaryIndustrialOrganization.build_family()


def diagram_provider() -> ModuleDiagramProvider:
    """Return the PIHC3-owned MIO trait-tree authoring provider."""

    return replace(
        MIO_DIAGRAM_PROVIDER,
        replaces_registered_provider=True,
    )
