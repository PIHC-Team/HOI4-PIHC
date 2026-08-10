"""PIHC3 continuous focus Entity extension."""

from __future__ import annotations

import heavenbase as hb

from paradev.build import SimpleSourceFamily, Slot


class PIHC3ContinuousFocusModule(hb.Entity):
    """One independently editable PIHC3 continuous focus module."""

    identifier = "pihc3-continuous-focus-module"
    module_id = (
        hb.field(hb.ShortText).default("").desc("Stable ParaDev module identifier.")
    )
    data = (
        hb.field(hb.Json)
        .default({})
        .desc("Structured metadata, localization, and resource references.")
    )
    family = "continuous_focus"
    resource_slots = (
        Slot(
            name="def",
            match="def.txt",
            required=True,
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
        family=PIHC3ContinuousFocusModule.family,
        source_slots=PIHC3ContinuousFocusModule.resource_slots,
        pdx_path_template="common/continuous_focus/{object_id}.txt",
        loc_path_template="localisation/{language_folder}/{object_id}_{language}.yml",
        required_loc_keys=("{object_id}", "{object_id}_desc"),
    )


__all__ = ["PIHC3ContinuousFocusModule", "build_family"]
