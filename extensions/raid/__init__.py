"""PIHC3 raid Entity extension."""

from __future__ import annotations

import heavenbase as hb

from paradev.build import SimpleSourceFamily, Slot


class PIHC3RaidModule(hb.Entity):
    """One independently editable PIHC3 raid module."""

    identifier = "pihc3-raid-module"
    module_id = (
        hb.field(hb.ShortText).default("").desc("Stable ParaDev module identifier.")
    )
    data = (
        hb.field(hb.Json)
        .default({})
        .desc("Structured metadata, localization, and resource references.")
    )
    family = "raid"
    resource_slots = (
        Slot(
            name="pdx",
            match="^common/raids/.*\\.txt$",
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
        family=PIHC3RaidModule.family,
        source_slots=PIHC3RaidModule.resource_slots,
        pdx_path_template="{source_path}",
        loc_path_template="localisation/{language_folder}/{object_id}_{language}.yml",
        visible=False,
    )


__all__ = ["PIHC3RaidModule", "build_family"]
