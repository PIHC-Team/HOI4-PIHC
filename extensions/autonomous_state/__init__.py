"""PIHC3 autonomous state Entity extension."""

from __future__ import annotations

import heavenbase as hb

from paradev.build import SimpleSourceFamily, Slot


class PIHC3AutonomousStateModule(hb.Entity):
    """One independently editable PIHC3 autonomous state module."""

    identifier = "pihc3-autonomous-state-module"
    module_id = (
        hb.field(hb.ShortText).default("").desc("Stable ParaDev module identifier.")
    )
    data = (
        hb.field(hb.Json)
        .default({})
        .desc("Structured metadata, localization, and resource references.")
    )
    family = "autonomous_state"
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
        family=PIHC3AutonomousStateModule.family,
        source_slots=PIHC3AutonomousStateModule.resource_slots,
        pdx_path_template="common/autonomous_states/{object_id}.txt",
        loc_path_template="localisation/{language_folder}/{object_id}_{language}.yml",
        required_loc_keys=("{object_id}", "{object_id}_desc"),
    )


__all__ = ["PIHC3AutonomousStateModule", "build_family"]
