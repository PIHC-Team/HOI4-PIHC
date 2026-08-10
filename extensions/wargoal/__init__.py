"""PIHC3 wargoal Entity extension."""

from __future__ import annotations

import heavenbase as hb

from paradev.build import SimpleSourceFamily, Slot


class PIHC3WargoalModule(hb.Entity):
    """One independently editable PIHC3 wargoal module."""

    identifier = "pihc3-wargoal-module"
    module_id = (
        hb.field(hb.ShortText).default("").desc("Stable ParaDev module identifier.")
    )
    data = (
        hb.field(hb.Json)
        .default({})
        .desc("Structured metadata, localization, and resource references.")
    )
    family = "wargoal"
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
        family=PIHC3WargoalModule.family,
        source_slots=PIHC3WargoalModule.resource_slots,
        pdx_path_template="common/wargoals/{object_id}.txt",
        loc_path_template="localisation/{language_folder}/{object_id}_{language}.yml",
        required_loc_keys=("{object_id}", "{object_id}_WAR_NAME", "{object_id}_desc"),
    )


__all__ = ["PIHC3WargoalModule", "build_family"]
