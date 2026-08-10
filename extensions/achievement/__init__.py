"""PIHC3 achievement Entity and compiler."""

from __future__ import annotations

import heavenbase as hb

from paradev.build import SimpleSourceFamily, Slot

_SOURCE_FORM_FIELD_HINTS = {
    "unique_id": {
        "label": {"default": "Achievement pack ID", "zh": "成就包 ID"},
        "description": {
            "default": "Stable Steam achievement-pack identifier shared by this project's achievements.",
            "zh": "本项目成就共用的稳定 Steam 成就包标识。",
        },
    },
    "possible": {
        "label": {"default": "Eligibility conditions", "zh": "成就资格条件"},
        "description": {
            "default": "Conditions that must hold for this achievement to remain eligible.",
            "zh": "此成就保持可解锁资格所必须满足的条件。",
        },
        "control": "block-text",
    },
    "happened": {
        "label": {"default": "Completion conditions", "zh": "成就完成条件"},
        "description": {
            "default": "Conditions that unlock this achievement once eligibility is established.",
            "zh": "满足成就资格后，用于判定解锁此成就的条件。",
        },
        "control": "block-text",
    },
    "hidden_trigger": {
        "label": {"default": "Hidden conditions", "zh": "隐藏条件"},
        "description": {
            "default": "Nested checks evaluated without exposing their details in the achievement UI.",
            "zh": "不会在成就界面显示具体内容的嵌套检查条件。",
        },
        "control": "block-text",
    },
}


class PIHC3Achievement(hb.Entity):
    """One independently editable PIHC3 achievement."""

    identifier = "pihc3-achievement"
    title = hb.field(hb.ShortText).default("")
    description = hb.field(hb.LongText).default("")
    family = "achievement"
    resource_slots = (
        Slot("def", "def.txt", required=True, kind="pdx"),
        Slot("loc", "**/*.loc", many=True, kind="loc"),
        Slot("preview", r"^icon\.(png|dds|tga)$", regex=True),
        Slot(
            "compiled_icons",
            r"^gfx/achievements/.*\.dds$",
            many=True,
            regex=True,
            kind="copy",
            authoring_path="gfx/achievements/{filename}",
        ),
    )
    compilation_hooks = ("normalize", "check", "emit")
    source_form_field_hints = _SOURCE_FORM_FIELD_HINTS

    @classmethod
    def build_family(cls) -> PIHC3AchievementFamily:
        """Return the achievement compiler."""

        return PIHC3AchievementFamily()


class PIHC3AchievementFamily(SimpleSourceFamily):
    """Compile achievements together with their owned icons."""

    replaces_registered_family = True
    source_form_field_hints = _SOURCE_FORM_FIELD_HINTS

    def __init__(self) -> None:
        super().__init__(
            family=PIHC3Achievement.family,
            pdx_path_template="common/achievements/{object_id}.txt",
            loc_path_template=(
                "localisation/{language_folder}/{object_id}_{language}.yml"
            ),
            copy_path_template="{source_path}",
            source_slots=PIHC3Achievement.resource_slots,
            required_loc_keys=("{object_id}_DESC", "{object_id}_NAME"),
        )


def build_family() -> PIHC3AchievementFamily:
    """HeavenBase Registry target for the achievement compiler."""

    return PIHC3Achievement.build_family()
