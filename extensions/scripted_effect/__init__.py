"""PIHC3 scripted effect Entity extension."""

from __future__ import annotations

import heavenbase as hb

from paradev.build import SimpleSourceFamily, Slot

_SOURCE_FORM_FIELD_HINTS = {
    "$root": {
        "label": {"default": "Effect body", "zh": "效果脚本"},
        "description": {
            "default": "Statements executed whenever this scripted effect is called.",
            "zh": "调用此脚本效果时执行的语句。",
        },
        "placeholder": {
            "default": "add_political_power = 10",
            "zh": "add_political_power = 10",
        },
        "control": "block-text",
    }
}


class PIHC3ScriptedEffectModule(hb.Entity):
    """One independently editable PIHC3 scripted effect module."""

    identifier = "pihc3-scripted-effect-module"
    module_id = hb.field(hb.ShortText).default("").desc("Stable ParaDev module identifier.")
    data = hb.field(hb.Json).default({}).desc("Structured metadata, localization, and resource references.")
    family = "scripted_effect"
    resource_slots = (
        Slot(
            name="def",
            match="def.txt",
            required=True,
            kind="pdx",
        ),
    )
    compilation_hooks = ("normalize", "check", "emit")
    source_form_field_hints = _SOURCE_FORM_FIELD_HINTS

    @classmethod
    def build_family(cls) -> PIHC3ScriptedEffectFamily:
        """Return the scripted-effect compiler owned by this Entity type.

        Args:
            None.

        Returns:
            PIHC3ScriptedEffectFamily: Registry-ready scripted-effect compiler.
        """

        return PIHC3ScriptedEffectFamily()


class PIHC3ScriptedEffectFamily(SimpleSourceFamily):
    """Compile scripted effects with Registry-declared body authoring."""

    source_form_field_hints = _SOURCE_FORM_FIELD_HINTS

    def __init__(self) -> None:
        super().__init__(
            family=PIHC3ScriptedEffectModule.family,
            source_slots=PIHC3ScriptedEffectModule.resource_slots,
            pdx_path_template="common/scripted_effects/{object_id}.txt",
        )


def build_family() -> PIHC3ScriptedEffectFamily:
    """Return the Registry compiler owned by this Entity extension.

    Args:
        None.

    Returns:
        PIHC3ScriptedEffectFamily: Registry-ready scripted-effect compiler.
    """

    return PIHC3ScriptedEffectModule.build_family()


__all__ = ["PIHC3ScriptedEffectFamily", "PIHC3ScriptedEffectModule", "build_family"]
