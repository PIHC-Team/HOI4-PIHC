"""PIHC3 resistance activity Entity extension."""

from __future__ import annotations

import heavenbase as hb

from paradev.build import SimpleSourceFamily, Slot


class PIHC3ResistanceActivityModule(hb.Entity):
    """One independently editable PIHC3 resistance activity module."""

    identifier = "pihc3-resistance-activity-module"
    module_id = (
        hb.field(hb.ShortText).default("").desc("Stable ParaDev module identifier.")
    )
    data = (
        hb.field(hb.Json)
        .default({})
        .desc("Structured metadata, localization, and resource references.")
    )
    family = "resistance_activity"
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
        family=PIHC3ResistanceActivityModule.family,
        source_slots=PIHC3ResistanceActivityModule.resource_slots,
        pdx_path_template="common/resistance_activity/{object_id}.txt",
        loc_path_template="localisation/{language_folder}/{object_id}_{language}.yml",
        required_loc_keys=("{object_id}_alert",),
    )


__all__ = ["PIHC3ResistanceActivityModule", "build_family"]
