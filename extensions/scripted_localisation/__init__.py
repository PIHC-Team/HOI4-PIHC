"""PIHC3 scripted localisation Entity extension."""

from __future__ import annotations

import heavenbase as hb

from paradev.build import SimpleSourceFamily, Slot


class PIHC3ScriptedLocalisationModule(hb.Entity):
    """One independently editable PIHC3 scripted localisation module."""

    identifier = "pihc3-scripted-localisation-module"
    module_id = (
        hb.field(hb.ShortText).default("").desc("Stable ParaDev module identifier.")
    )
    data = (
        hb.field(hb.Json)
        .default({})
        .desc("Structured metadata, localization, and resource references.")
    )
    family = "scripted_localisation"
    resource_slots = (
        Slot(
            name="pdx",
            match="^common/scripted_localisation/.*\\.txt$",
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
        family=PIHC3ScriptedLocalisationModule.family,
        source_slots=PIHC3ScriptedLocalisationModule.resource_slots,
        pdx_path_template="{source_path}",
        visible=False,
    )


__all__ = ["PIHC3ScriptedLocalisationModule", "build_family"]
