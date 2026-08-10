"""PIHC3 intelligence agency Entity extension."""

from __future__ import annotations

import heavenbase as hb

from paradev.build import SimpleSourceFamily, Slot


class PIHC3IntelligenceAgencyModule(hb.Entity):
    """One independently editable PIHC3 intelligence agency module."""

    identifier = "pihc3-intelligence-agency-module"
    module_id = (
        hb.field(hb.ShortText).default("").desc("Stable ParaDev module identifier.")
    )
    data = (
        hb.field(hb.Json)
        .default({})
        .desc("Structured metadata, localization, and resource references.")
    )
    family = "intelligence_agency"
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
            name="preview",
            match="^icon\\.(png|dds|tga)$",
            regex=True,
        ),
        Slot(
            name="compiled_assets",
            match="^interface/intelligence_agencies/.*\\.gfx$",
            many=True,
            regex=True,
            kind="copy",
            authoring_path="interface/intelligence_agencies/{filename}",
        ),
        Slot(
            name="compiled_assets",
            match="^gfx/interface/intelligence_agencies/.*\\.dds$",
            many=True,
            regex=True,
            kind="copy",
            authoring_path="gfx/interface/intelligence_agencies/{filename}",
        ),
    )
    compilation_hooks = ("normalize", "check", "emit")


def build_family() -> SimpleSourceFamily:
    """Return the Registry compiler owned by this Entity extension."""

    return SimpleSourceFamily(
        family=PIHC3IntelligenceAgencyModule.family,
        source_slots=PIHC3IntelligenceAgencyModule.resource_slots,
        pdx_path_template="common/intelligence_agencies/{object_id}.txt",
        loc_path_template="localisation/{language_folder}/{object_id}_{language}.yml",
        copy_path_template="{source_path}",
        required_loc_keys=("{object_id}", "{object_id}_desc"),
        title_loc_keys=("{object_id}_NAME", "{object_id}"),
    )


__all__ = ["PIHC3IntelligenceAgencyModule", "build_family"]
