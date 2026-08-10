"""PIHC3 leader trait Entity extension."""

from __future__ import annotations

import heavenbase as hb

from paradev.build import SimpleSourceFamily, Slot


class PIHC3LeaderTraitModule(hb.Entity):
    """One independently editable PIHC3 leader trait module."""

    identifier = "pihc3-leader-trait-module"
    module_id = (
        hb.field(hb.ShortText).default("").desc("Stable ParaDev module identifier.")
    )
    data = (
        hb.field(hb.Json)
        .default({})
        .desc("Structured metadata, localization, and resource references.")
    )
    family = "leader_trait"
    resource_slots = (
        Slot(
            name="pdx",
            match="^common/country_leader/(00_traits|toa_traits)\\.txt$|^common/scientist_traits/.*\\.txt$",
            required=True,
            many=True,
            regex=True,
            kind="pdx",
        ),
    )
    compilation_hooks = ("normalize", "check", "emit")


def build_family() -> SimpleSourceFamily:
    """Return the Registry compiler owned by this Entity extension."""

    return SimpleSourceFamily(
        family=PIHC3LeaderTraitModule.family,
        source_slots=PIHC3LeaderTraitModule.resource_slots,
        pdx_path_template="{source_path}",
        visible=False,
    )


__all__ = ["PIHC3LeaderTraitModule", "build_family"]
