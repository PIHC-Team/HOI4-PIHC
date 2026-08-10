"""PIHC3 portrait Entity extension."""

from __future__ import annotations

import heavenbase as hb

from paradev.build import SimpleSourceFamily, Slot


class PIHC3PortraitModule(hb.Entity):
    """One independently editable PIHC3 portrait module."""

    identifier = "pihc3-portrait-module"
    module_id = (
        hb.field(hb.ShortText).default("").desc("Stable ParaDev module identifier.")
    )
    data = (
        hb.field(hb.Json)
        .default({})
        .desc("Structured metadata, localization, and resource references.")
    )
    family = "portrait"
    resource_slots = (
        Slot(
            name="definitions",
            match="^portraits/.*\\.txt$",
            many=True,
            regex=True,
            kind="pdx",
        ),
        Slot(
            name="assets",
            match="^gfx/leaders/.*\\.dds$",
            many=True,
            regex=True,
            kind="copy",
            authoring_path="gfx/leaders/{filename}",
        ),
        Slot(
            name="assets",
            match="^interface/portraits/.*\\.gfx$",
            many=True,
            regex=True,
            kind="copy",
            authoring_path="interface/portraits/{filename}",
        ),
    )
    compilation_hooks = ("normalize", "check", "emit")


def build_family() -> SimpleSourceFamily:
    """Return the Registry compiler owned by this Entity extension."""

    return SimpleSourceFamily(
        family=PIHC3PortraitModule.family,
        source_slots=PIHC3PortraitModule.resource_slots,
        pdx_path_template="{source_path}",
        copy_path_template="{source_path}",
    )


__all__ = ["PIHC3PortraitModule", "build_family"]
