"""PIHC3 general history Entity extension."""

from __future__ import annotations

import heavenbase as hb

from paradev.build import SimpleSourceFamily, Slot


class PIHC3GeneralHistoryModule(hb.Entity):
    """One independently editable PIHC3 general history module."""

    identifier = "pihc3-general-history-module"
    module_id = (
        hb.field(hb.ShortText).default("").desc("Stable ParaDev module identifier.")
    )
    data = (
        hb.field(hb.Json)
        .default({})
        .desc("Structured metadata, localization, and resource references.")
    )
    family = "general_history"
    resource_slots = (
        Slot(
            name="pdx",
            match="^history/general/.*\\.txt$",
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
        family=PIHC3GeneralHistoryModule.family,
        source_slots=PIHC3GeneralHistoryModule.resource_slots,
        pdx_path_template="{source_path}",
        visible=False,
    )


__all__ = ["PIHC3GeneralHistoryModule", "build_family"]
