"""PIHC3 country history Entity extension."""

from __future__ import annotations

import heavenbase as hb

from paradev.build import SimpleSourceFamily, Slot


class PIHC3CountryHistoryModule(hb.Entity):
    """One independently editable PIHC3 country history module."""

    identifier = "pihc3-country-history-module"
    module_id = (
        hb.field(hb.ShortText).default("").desc("Stable ParaDev module identifier.")
    )
    data = (
        hb.field(hb.Json)
        .default({})
        .desc("Structured metadata, localization, and resource references.")
    )
    family = "country_history"
    resource_slots = (
        Slot(
            name="pdx",
            match="^(common/country_tags|common/country_tag_aliases|common/countries|history/countries)/.*\\.txt$",
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
        family=PIHC3CountryHistoryModule.family,
        source_slots=PIHC3CountryHistoryModule.resource_slots,
        pdx_path_template="{source_path}",
        loc_path_template="localisation/{language_folder}/{object_id}_{language}.yml",
        visible=False,
    )


__all__ = ["PIHC3CountryHistoryModule", "build_family"]
