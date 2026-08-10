"""PIHC3 scripted gui Entity extension."""

from __future__ import annotations

import heavenbase as hb

from paradev.build import SimpleSourceFamily, Slot

_SOURCE_FORM_FIELD_HINTS = {
    "visible": {
        "label": {"default": "Visibility conditions", "zh": "显示条件"},
        "description": {
            "default": "Conditions controlling whether this scripted GUI is visible.",
            "zh": "控制此脚本界面是否显示的条件。",
        },
        "control": "block-text",
    },
    "triggers": {
        "label": {"default": "Named triggers", "zh": "命名触发器"},
        "description": {
            "default": "Named trigger blocks exposed by this scripted GUI.",
            "zh": "此脚本界面提供的命名触发器块。",
        },
        "control": "block-text",
    },
    "effects": {
        "label": {"default": "Named effects", "zh": "命名效果"},
        "description": {
            "default": "Named effect blocks exposed by this scripted GUI.",
            "zh": "此脚本界面提供的命名效果块。",
        },
        "control": "block-text",
    },
    "properties": {
        "label": {"default": "Properties", "zh": "属性"},
        "description": {
            "default": "Named properties exposed by this scripted GUI.",
            "zh": "此脚本界面提供的命名属性。",
        },
        "control": "block-text",
    },
}


class PIHC3ScriptedGuiModule(hb.Entity):
    """One independently editable PIHC3 scripted gui module."""

    identifier = "pihc3-scripted-gui-module"
    module_id = hb.field(hb.ShortText).default("").desc("Stable ParaDev module identifier.")
    data = hb.field(hb.Json).default({}).desc("Structured metadata, localization, and resource references.")
    family = "scripted_gui"
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
    def build_family(cls) -> PIHC3ScriptedGuiFamily:
        """Return the scripted-GUI compiler owned by this Entity type.

        Args:
            None.

        Returns:
            PIHC3ScriptedGuiFamily: Registry-ready scripted-GUI compiler.
        """

        return PIHC3ScriptedGuiFamily()


class PIHC3ScriptedGuiFamily(SimpleSourceFamily):
    """Compile scripted GUIs with Registry-declared block authoring."""

    source_form_field_hints = _SOURCE_FORM_FIELD_HINTS

    def __init__(self) -> None:
        super().__init__(
            family=PIHC3ScriptedGuiModule.family,
            source_slots=PIHC3ScriptedGuiModule.resource_slots,
            pdx_path_template="common/scripted_guis/{object_id}.txt",
        )


def build_family() -> PIHC3ScriptedGuiFamily:
    """Return the Registry compiler owned by this Entity extension.

    Args:
        None.

    Returns:
        PIHC3ScriptedGuiFamily: Registry-ready scripted-GUI compiler.
    """

    return PIHC3ScriptedGuiModule.build_family()


__all__ = ["PIHC3ScriptedGuiFamily", "PIHC3ScriptedGuiModule", "build_family"]
