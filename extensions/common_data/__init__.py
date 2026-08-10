"""PIHC3 common data Entity extension."""

from __future__ import annotations

import heavenbase as hb

from paradev.build import SimpleSourceFamily, Slot


class PIHC3CommonDataModule(hb.Entity):
    """One independently editable PIHC3 common data module."""

    identifier = "pihc3-common-data-module"
    module_id = (
        hb.field(hb.ShortText).default("").desc("Stable ParaDev module identifier.")
    )
    data = (
        hb.field(hb.Json)
        .default({})
        .desc("Structured metadata, localization, and resource references.")
    )
    family = "common_data"
    resource_slots = (
        Slot(
            name="pdx",
            match="^common/(abilities|aces|collections|equipment_groups|generation|idea_tags|intelligence_agency_upgrades|medals|modifier_definitions|mtth|names|occupation_laws|resistance_compliance_modifiers|scorers|scripted_diplomatic_actions|script_constants|state_category|synchronized_dynamic_tokens|technology_sharing|technology_tags|terrain|timed_activities|unit_tags)/.*\\.txt$|^common/(alerts|combat_tactics|event_modifiers|script_enums|triggered_modifiers|weather)\\.txt$|^common/units/(equipment/upgrades|names|names_railway_guns)/.*\\.txt$",
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
        family=PIHC3CommonDataModule.family,
        source_slots=PIHC3CommonDataModule.resource_slots,
        pdx_path_template="{source_path}",
        loc_path_template="localisation/{language_folder}/{object_id}_{language}.yml",
        visible=False,
    )


__all__ = ["PIHC3CommonDataModule", "build_family"]
