"""PIHC3 unit Entity extension."""

from __future__ import annotations

import heavenbase as hb

from paradev.build import SimpleSourceFamily, Slot


class PIHC3UnitModule(hb.Entity):
    """One independently editable PIHC3 unit module."""

    identifier = "pihc3-unit-module"
    module_id = (
        hb.field(hb.ShortText).default("").desc("Stable ParaDev module identifier.")
    )
    data = (
        hb.field(hb.Json)
        .default({})
        .desc("Structured metadata, localization, and resource references.")
    )
    family = "unit"
    resource_slots = (
        Slot(
            name="pdx",
            match="^common/units/(air|battlecruiser|battleship|cannon|carrier|destroyer|engineer|field_hospital|heavy_cruiser|hq_support|infantry|light_cruiser|logistics|maintenance|military_police|recon|repair_ships|signal|submarine|support_ships|tank)\\.txt$|^common/units/equipment/(convoys|repair_ships|ship_hull_carrier|ship_hull_cruiser|ship_hull_heavy|ship_hull_light|ship_hull_submarine|support_ships|trains)\\.txt$|^common/units/unit_modifiers/.*\\.txt$",
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
        family=PIHC3UnitModule.family,
        source_slots=PIHC3UnitModule.resource_slots,
        pdx_path_template="{source_path}",
        loc_path_template="localisation/{language_folder}/{object_id}_{language}.yml",
        visible=False,
    )


__all__ = ["PIHC3UnitModule", "build_family"]
