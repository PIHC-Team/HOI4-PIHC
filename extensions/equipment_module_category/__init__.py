"""PIHC3 equipment module category Entity extension."""

from __future__ import annotations

import heavenbase as hb

from paradev.build import SimpleSourceFamily, Slot


class PIHC3EquipmentModuleCategoryModule(hb.Entity):
    """One independently editable PIHC3 equipment module category module."""

    identifier = "pihc3-equipment-module-category-module"
    module_id = (
        hb.field(hb.ShortText).default("").desc("Stable ParaDev module identifier.")
    )
    data = (
        hb.field(hb.Json)
        .default({})
        .desc("Structured metadata, localization, and resource references.")
    )
    family = "equipment_module_category"
    resource_slots = (
        Slot(
            name="loc",
            match="**/*.loc",
            many=True,
            kind="loc",
        ),
        Slot(
            name="icon",
            match="icon.png",
            kind="copy",
            authoring_path="{filename}",
        ),
        Slot(
            name="icon",
            match="^icon\\.(dds|tga)$",
            regex=True,
            kind="copy",
            authoring_path="{filename}",
        ),
    )
    compilation_hooks = ("normalize", "check", "emit")


def build_family() -> SimpleSourceFamily:
    """Return the Registry compiler owned by this Entity extension."""

    return SimpleSourceFamily(
        family=PIHC3EquipmentModuleCategoryModule.family,
        source_slots=PIHC3EquipmentModuleCategoryModule.resource_slots,
        loc_path_template="localisation/{language_folder}/EQ_MOD_CAT_{object_id}_TITLE_{language}.yml",
        copy_path_template="gfx/interface/modules/GFX_EMI_{object_id}{source_suffix}",
        sprite_gfx_path_template="interface/PIHC3_equipment_module_categories.gfx",
        sprite_name_template="GFX_EMI_{object_id}",
        required_loc_keys=("EQ_MOD_CAT_{object_id}_TITLE",),
        sprite_slots=("icon",),
    )


__all__ = ["PIHC3EquipmentModuleCategoryModule", "build_family"]
