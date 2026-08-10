"""PIHC3 difficulty setting Entity extension."""

from __future__ import annotations

import heavenbase as hb

from paradev.build import SimpleSourceFamily, Slot


class PIHC3DifficultySettingModule(hb.Entity):
    """One independently editable PIHC3 difficulty setting module."""

    identifier = "pihc3-difficulty-setting-module"
    module_id = (
        hb.field(hb.ShortText).default("").desc("Stable ParaDev module identifier.")
    )
    data = (
        hb.field(hb.Json)
        .default({})
        .desc("Structured metadata, localization, and resource references.")
    )
    family = "difficulty_setting"
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
        family=PIHC3DifficultySettingModule.family,
        source_slots=PIHC3DifficultySettingModule.resource_slots,
        pdx_path_template="common/difficulty_settings/{object_id}.txt",
        loc_path_template="localisation/{language_folder}/{object_id}_{language}.yml",
    )


__all__ = ["PIHC3DifficultySettingModule", "build_family"]
