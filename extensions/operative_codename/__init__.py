"""PIHC3 operative codename Entity extension."""

from __future__ import annotations

import heavenbase as hb

from paradev.build import SimpleSourceFamily, Slot


class PIHC3OperativeCodenameModule(hb.Entity):
    """One independently editable PIHC3 operative codename module."""

    identifier = "pihc3-operative-codename-module"
    module_id = (
        hb.field(hb.ShortText).default("").desc("Stable ParaDev module identifier.")
    )
    data = (
        hb.field(hb.Json)
        .default({})
        .desc("Structured metadata, localization, and resource references.")
    )
    family = "operative_codename"
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
        family=PIHC3OperativeCodenameModule.family,
        source_slots=PIHC3OperativeCodenameModule.resource_slots,
        pdx_path_template="common/units/codenames_operatives/{object_id}.txt",
        loc_path_template="localisation/{language_folder}/{object_id}_{language}.yml",
        required_loc_keys=("{object_id}_NAME_THEME",),
        title_loc_keys=("{object_id}_NAME_THEME",),
    )


__all__ = ["PIHC3OperativeCodenameModule", "build_family"]
