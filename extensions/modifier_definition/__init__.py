"""PIHC3 modifier definition Entity extension."""

from __future__ import annotations

import heavenbase as hb

from paradev.build import SimpleSourceFamily, Slot


class PIHC3ModifierDefinitionModule(hb.Entity):
    """One independently editable PIHC3 modifier definition module."""

    identifier = "pihc3-modifier-definition-module"
    module_id = (
        hb.field(hb.ShortText).default("").desc("Stable ParaDev module identifier.")
    )
    data = (
        hb.field(hb.Json)
        .default({})
        .desc("Structured metadata, localization, and resource references.")
    )
    family = "modifier_definition"
    resource_slots = (
        Slot(
            name="pdx",
            match="^(common/dynamic_modifiers|common/opinion_modifiers|common/peace_conference/cost_modifiers)/.*\\.txt$",
            required=True,
            many=True,
            regex=True,
            kind="pdx",
        ),
        Slot(
            name="loc",
            match="**/*.loc",
            many=True,
            kind="loc",
        ),
    )
    compilation_hooks = ("normalize", "check", "emit")


def build_family() -> SimpleSourceFamily:
    """Return the Registry compiler owned by this Entity extension."""

    return SimpleSourceFamily(
        family=PIHC3ModifierDefinitionModule.family,
        source_slots=PIHC3ModifierDefinitionModule.resource_slots,
        pdx_path_template="{source_path}",
        loc_path_template="localisation/{language_folder}/{object_id}_{language}.yml",
        visible=False,
    )


__all__ = ["PIHC3ModifierDefinitionModule", "build_family"]
