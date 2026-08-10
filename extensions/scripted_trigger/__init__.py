"""PIHC3 scripted trigger Entity extension."""

from __future__ import annotations

import heavenbase as hb

from paradev.build import SimpleSourceFamily, Slot

_SOURCE_FORM_FIELD_HINTS = {
    "$root": {
        "label": {"default": "Trigger conditions", "zh": "触发条件"},
        "description": {
            "default": "Conditions evaluated whenever this scripted trigger is called.",
            "zh": "调用此脚本触发器时检查的条件。",
        },
        "placeholder": {"default": "always = yes", "zh": "always = yes"},
        "control": "block-text",
    }
}


class PIHC3ScriptedTriggerModule(hb.Entity):
    """One independently editable PIHC3 scripted trigger module."""

    identifier = "pihc3-scripted-trigger-module"
    module_id = hb.field(hb.ShortText).default("").desc("Stable ParaDev module identifier.")
    data = hb.field(hb.Json).default({}).desc("Structured metadata, localization, and resource references.")
    family = "scripted_trigger"
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
    def build_family(cls) -> PIHC3ScriptedTriggerFamily:
        """Return the scripted-trigger compiler owned by this Entity type.

        Args:
            None.

        Returns:
            PIHC3ScriptedTriggerFamily: Registry-ready scripted-trigger compiler.
        """

        return PIHC3ScriptedTriggerFamily()


class PIHC3ScriptedTriggerFamily(SimpleSourceFamily):
    """Compile scripted triggers with Registry-declared body authoring."""

    source_form_field_hints = _SOURCE_FORM_FIELD_HINTS

    def __init__(self) -> None:
        super().__init__(
            family=PIHC3ScriptedTriggerModule.family,
            source_slots=PIHC3ScriptedTriggerModule.resource_slots,
            pdx_path_template="common/scripted_triggers/{object_id}.txt",
        )


def build_family() -> PIHC3ScriptedTriggerFamily:
    """Return the Registry compiler owned by this Entity extension.

    Args:
        None.

    Returns:
        PIHC3ScriptedTriggerFamily: Registry-ready scripted-trigger compiler.
    """

    return PIHC3ScriptedTriggerModule.build_family()


__all__ = ["PIHC3ScriptedTriggerFamily", "PIHC3ScriptedTriggerModule", "build_family"]
