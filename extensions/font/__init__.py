"""PIHC3 font Entity extension."""

from __future__ import annotations

import heavenbase as hb

from paradev.build import SimpleSourceFamily, Slot


class PIHC3FontModule(hb.Entity):
    """One independently editable PIHC3 font module."""

    identifier = "pihc3-font-module"
    module_id = (
        hb.field(hb.ShortText).default("").desc("Stable ParaDev module identifier.")
    )
    data = (
        hb.field(hb.Json)
        .default({})
        .desc("Structured metadata, localization, and resource references.")
    )
    family = "font"
    resource_slots = (
        Slot(
            name="assets",
            match="^gfx/fonts/.*\\.(fnt|dds|tga)$",
            required=True,
            many=True,
            regex=True,
            kind="copy",
            authoring_path="gfx/fonts/{filename}",
        ),
    )
    compilation_hooks = ("normalize", "check", "emit")


def build_family() -> SimpleSourceFamily:
    """Return the Registry compiler owned by this Entity extension."""

    return SimpleSourceFamily(
        family=PIHC3FontModule.family,
        source_slots=PIHC3FontModule.resource_slots,
        copy_path_template="{source_path}",
        visible=False,
    )


__all__ = ["PIHC3FontModule", "build_family"]
