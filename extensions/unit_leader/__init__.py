"""PIHC3 unit leader Entity extension."""

from __future__ import annotations

import heavenbase as hb

from paradev.build import SimpleSourceFamily, Slot


class PIHC3UnitLeaderModule(hb.Entity):
    """One independently editable PIHC3 unit leader module."""

    identifier = "pihc3-unit-leader-module"
    module_id = (
        hb.field(hb.ShortText).default("").desc("Stable ParaDev module identifier.")
    )
    data = (
        hb.field(hb.Json)
        .default({})
        .desc("Structured metadata, localization, and resource references.")
    )
    family = "unit_leader"
    resource_slots = (
        Slot(
            name="pdx",
            match="^common/unit_leader/.*\\.txt$",
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
        family=PIHC3UnitLeaderModule.family,
        source_slots=PIHC3UnitLeaderModule.resource_slots,
        pdx_path_template="{source_path}",
        visible=False,
    )


__all__ = ["PIHC3UnitLeaderModule", "build_family"]
