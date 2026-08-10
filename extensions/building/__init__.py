"""PIHC3 building Entity extension."""

from __future__ import annotations

import heavenbase as hb

from paradev.build import SimpleSourceFamily, Slot


class PIHC3BuildingModule(hb.Entity):
    """One independently editable PIHC3 building module."""

    identifier = "pihc3-building-module"
    module_id = (
        hb.field(hb.ShortText).default("").desc("Stable ParaDev module identifier.")
    )
    data = (
        hb.field(hb.Json)
        .default({})
        .desc("Structured metadata, localization, and resource references.")
    )
    family = "building"
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
        Slot(
            name="icon",
            match="^icon\\.(png|dds|tga)$",
            regex=True,
            kind="copy",
            authoring_path="{filename}",
        ),
    )
    compilation_hooks = ("normalize", "check", "emit")


def build_family() -> SimpleSourceFamily:
    """Return the Registry compiler owned by this Entity extension."""

    return SimpleSourceFamily(
        family=PIHC3BuildingModule.family,
        source_slots=PIHC3BuildingModule.resource_slots,
        pdx_path_template="common/buildings/{object_id}.txt",
        loc_path_template="localisation/{language_folder}/{object_id}_{language}.yml",
        required_loc_keys=("{object_id}", "{object_id}_desc"),
        title_loc_keys=(),
    )


__all__ = ["PIHC3BuildingModule", "build_family"]
