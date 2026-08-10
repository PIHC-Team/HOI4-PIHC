"""PIHC3 on action Entity extension."""

from __future__ import annotations

import heavenbase as hb

from paradev.build import SimpleSourceFamily, Slot

_SOURCE_FORM_FIELD_HINTS = {
    "$root": {
        "label": {"default": "On-action definitions", "zh": "On-action 定义"},
        "description": {
            "default": "Hooks and statements contained in this on-action module.",
            "zh": "此 on-action 模块包含的钩子和执行语句。",
        },
        "placeholder": {
            "default": "on_monthly = { effect = { country_event = { id = my_event.1 } } }",
            "zh": "on_monthly = { effect = { country_event = { id = my_event.1 } } }",
        },
        "control": "block-text",
    }
}


class PIHC3OnActionModule(hb.Entity):
    """One independently editable PIHC3 on action module."""

    identifier = "pihc3-on-action-module"
    module_id = hb.field(hb.ShortText).default("").desc("Stable ParaDev module identifier.")
    data = hb.field(hb.Json).default({}).desc("Structured metadata, localization, and resource references.")
    family = "on_action"
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
    def build_family(cls) -> PIHC3OnActionFamily:
        """Return the on-action compiler owned by this Entity type.

        Args:
            None.

        Returns:
            PIHC3OnActionFamily: Registry-ready on-action compiler.
        """

        return PIHC3OnActionFamily()


class PIHC3OnActionFamily(SimpleSourceFamily):
    """Compile on-actions with Registry-declared effect authoring."""

    source_form_field_hints = _SOURCE_FORM_FIELD_HINTS

    def __init__(self) -> None:
        super().__init__(
            family=PIHC3OnActionModule.family,
            source_slots=PIHC3OnActionModule.resource_slots,
            pdx_path_template="common/on_actions/{object_id}.txt",
        )


def build_family() -> PIHC3OnActionFamily:
    """Return the Registry compiler owned by this Entity extension.

    Args:
        None.

    Returns:
        PIHC3OnActionFamily: Registry-ready on-action compiler.
    """

    return PIHC3OnActionModule.build_family()


__all__ = ["PIHC3OnActionFamily", "PIHC3OnActionModule", "build_family"]
