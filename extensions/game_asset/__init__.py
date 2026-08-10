"""PIHC3 game asset Entity extension."""

from __future__ import annotations

import heavenbase as hb

from paradev.build import SimpleSourceFamily, Slot


class PIHC3GameAssetModule(hb.Entity):
    """One independently editable PIHC3 game asset module."""

    identifier = "pihc3-game-asset-module"
    module_id = (
        hb.field(hb.ShortText).default("").desc("Stable ParaDev module identifier.")
    )
    data = (
        hb.field(hb.Json)
        .default({})
        .desc("Structured metadata, localization, and resource references.")
    )
    family = "game_asset"
    resource_slots = (
        Slot(
            name="pdx",
            match="^(country_metadata|tutorial)/.*\\.txt$|^common/national_focus/00_titlebar_styles\\.txt$|^gfx/interface/equipmentdesigner/graphic_db/.*\\.txt$",
            many=True,
            regex=True,
            kind="pdx",
        ),
        Slot(
            name="assets",
            match="^common/achievements\\.txt$|^gfx/(army_icons/army_icons\\.txt|entities/(buildings\\.(asset|gfx)|mapitems\\.(asset|gfx)|weather_entities\\.asset)|maparrows/([^/]+\\.dds|maparrows\\.txt)|minimap/minimap\\.dds|particles/(entities|environment)/[^/]+\\.(asset|gfx|NUDGE)|train_gfx_database/NSB_generic\\.txt)$|^gfx/FX/((buttonstate_nodowneffect|maparrow|pdxmap|river)\\.shader|constants\\.fxh)$|^gfx/models/(border_(bottom_)?mesh\\.mesh|borderlp_(bottom|top) material_(color|norm|spec)\\.dds|nambugame_nambu mat_(color|norm|spec)\\.dds|paper_(normal|spec|texture)\\.dds|wood_table_texture\\.dds)$|^dlc/dlc034_no_step_back/gfx/train_gfx_database/NSB_generic\\.txt$|^dlc/dlc036_by_blood_alone/gfx/entities/BBA_units_vehicles\\.asset$|^map/[^/]+\\.(bmp|csv|json|map|png|txt)$|^map/terrain/[^/]+\\.(bmp|dds|png)$|^thumbnail\\.png$",
            many=True,
            regex=True,
            kind="copy",
        ),
    )
    compilation_hooks = ("normalize", "check", "emit")


def build_family() -> SimpleSourceFamily:
    """Return the Registry compiler owned by this Entity extension."""

    return SimpleSourceFamily(
        family=PIHC3GameAssetModule.family,
        source_slots=PIHC3GameAssetModule.resource_slots,
        pdx_path_template="{source_path}",
        copy_path_template="{source_path}",
        visible=False,
    )


__all__ = ["PIHC3GameAssetModule", "build_family"]
