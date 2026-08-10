"""PIHC3 character Entity and compiler."""

from __future__ import annotations

from typing import ClassVar

import heavenbase as hb

from paradev.build import SimpleSourceFamily, Slot


class PIHC3Character(hb.Entity):
    """One independently editable PIHC3 character."""

    identifier = "pihc3-character"
    title = hb.field(hb.ShortText).default("")
    description = hb.field(hb.LongText).default("")
    family = "character"
    resource_slots = (
        Slot("def", "def.txt", required=True, kind="pdx"),
        Slot("loc", "**/*.loc", many=True, kind="loc"),
        Slot("preview", "portrait.png"),
        Slot(
            "compiled_portraits",
            r"^gfx/leaders/.*\.dds$",
            many=True,
            regex=True,
            kind="copy",
            authoring_path="gfx/leaders/{filename}",
        ),
        Slot(
            "compiled_portraits",
            r"^interface/portraits/.*\.gfx$",
            many=True,
            regex=True,
            kind="copy",
            authoring_path="interface/portraits/{filename}",
        ),
    )
    compilation_hooks = ("normalize", "check", "emit")
    # HeavenBase Entity annotations are logical fields; protocol metadata stays unannotated.
    source_form_field_hints = {  # noqa: RUF012
        "gender": {
            "description": {
                "default": "Character gender token: female, male, or undefined.",
                "zh": "角色性别标识：female、male 或 undefined。",
            }
        },
        "idea_token": {
            "description": {
                "default": "Stable token used when this character is referenced as an advisor idea.",
                "zh": "当该角色作为顾问理念被引用时使用的稳定标识。",
            }
        },
        "can_be_fired": {
            "description": {
                "default": "Whether the player may dismiss this advisor.",
                "zh": "玩家是否可以解雇该顾问。",
            }
        },
        "cost": {
            "description": {
                "default": "Political-power cost to appoint this advisor.",
                "zh": "任命该顾问所需的政治点数。",
            }
        },
        "removal_cost": {
            "description": {
                "default": "Political-power cost to remove this advisor; -1 prevents removal.",
                "zh": "移除该顾问的政治点数代价；-1 表示不可移除。",
            }
        },
    }

    @classmethod
    def build_family(cls) -> "PIHC3CharacterFamily":
        """Return the character compiler."""

        return PIHC3CharacterFamily()


class PIHC3CharacterFamily(SimpleSourceFamily):
    """Compile characters together with their owned portraits."""

    replaces_registered_family = True
    source_form_field_hints: ClassVar[dict[str, dict[str, object]]] = PIHC3Character.source_form_field_hints

    def __init__(self) -> None:
        super().__init__(
            family=PIHC3Character.family,
            pdx_path_template="common/characters/{object_id}.txt",
            loc_path_template=("localisation/{language_folder}/{object_id}_{language}.yml"),
            copy_path_template="{source_path}",
            source_slots=PIHC3Character.resource_slots,
            required_loc_keys=("{object_id}_DESC", "{object_id}_NAME"),
        )


def build_family() -> PIHC3CharacterFamily:
    """HeavenBase Registry target for the character compiler."""

    return PIHC3Character.build_family()
