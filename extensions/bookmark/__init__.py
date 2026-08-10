"""PIHC3 bookmark Entity extension."""

from __future__ import annotations

import heavenbase as hb

from paradev.build import SimpleSourceFamily, Slot


class PIHC3BookmarkModule(hb.Entity):
    """One independently editable PIHC3 bookmark module."""

    identifier = "pihc3-bookmark-module"
    module_id = (
        hb.field(hb.ShortText).default("").desc("Stable ParaDev module identifier.")
    )
    data = (
        hb.field(hb.Json)
        .default({})
        .desc("Structured metadata, localization, and resource references.")
    )
    family = "bookmark"
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
            name="picture",
            match="^gfx/interface/bookmarks/.*\\.dds$",
            regex=True,
            kind="copy",
            authoring_path="gfx/interface/bookmarks/{filename}",
        ),
    )
    compilation_hooks = ("normalize", "check", "emit")


def build_family() -> SimpleSourceFamily:
    """Return the Registry compiler owned by this Entity extension."""

    return SimpleSourceFamily(
        family=PIHC3BookmarkModule.family,
        source_slots=PIHC3BookmarkModule.resource_slots,
        pdx_path_template="common/bookmarks/{object_id}.txt",
        loc_path_template="localisation/{language_folder}/{object_id}_{language}.yml",
        copy_path_template="{source_path}",
        required_loc_keys=("{object_id}_NAME", "{object_id}_DESC"),
    )


__all__ = ["PIHC3BookmarkModule", "build_family"]
