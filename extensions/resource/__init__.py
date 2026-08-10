"""PIHC3 resource Entity extension."""

from __future__ import annotations

import heavenbase as hb

from paradev.build import SimpleSourceFamily, Slot


class PIHC3ResourceModule(hb.Entity):
    """One independently editable PIHC3 resource module."""

    identifier = "pihc3-resource-module"
    module_id = (
        hb.field(hb.ShortText).default("").desc("Stable ParaDev module identifier.")
    )
    data = (
        hb.field(hb.Json)
        .default({})
        .desc("Structured metadata, localization, and resource references.")
    )
    family = "resource"
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
        family=PIHC3ResourceModule.family,
        source_slots=PIHC3ResourceModule.resource_slots,
        pdx_path_template="common/resources/{object_id}.txt",
        loc_path_template="localisation/{language_folder}/{object_id}_{language}.yml",
        required_loc_keys=(
            "{object_id}_desc",
            "country_resource_{object_id}",
            "country_resource_cost_{object_id}",
        ),
    )


__all__ = ["PIHC3ResourceModule", "build_family"]
