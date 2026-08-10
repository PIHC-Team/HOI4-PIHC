"""PIHC3 AI configuration Entity extension."""

from __future__ import annotations

import heavenbase as hb

from paradev.build import SimpleSourceFamily, Slot


class PIHC3AiConfigModule(hb.Entity):
    """One independently editable PIHC3 AI configuration module."""

    identifier = "pihc3-ai-config-module"
    module_id = (
        hb.field(hb.ShortText).default("").desc("Stable ParaDev module identifier.")
    )
    data = (
        hb.field(hb.Json)
        .default({})
        .desc("Structured metadata, localization, and resource references.")
    )
    family = "ai_config"
    resource_slots = (
        Slot(
            name="pdx",
            match="^common/(ai_equipments|ai_faction_theaters|ai_focuses|ai_navy|ai_strategy|ai_strategy_plans|ai_templates)/.*\\.txt$|^common/(ai_attitudes|ai_personalities)\\.txt$",
            required=True,
            many=True,
            regex=True,
            kind="pdx",
        ),
    )
    compilation_hooks = ("normalize", "check", "emit")


def build_family() -> SimpleSourceFamily:
    """Return the Registry compiler owned by this Entity extension."""

    return SimpleSourceFamily(
        family=PIHC3AiConfigModule.family,
        source_slots=PIHC3AiConfigModule.resource_slots,
        pdx_path_template="{source_path}",
        visible=False,
    )


__all__ = ["PIHC3AiConfigModule", "build_family"]
