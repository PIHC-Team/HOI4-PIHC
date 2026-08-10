"""PIHC3 interface Entity extension."""

from __future__ import annotations

import heavenbase as hb

from paradev.build import SimpleSourceFamily, Slot


class PIHC3InterfaceModule(hb.Entity):
    """One independently editable PIHC3 interface module."""

    identifier = "pihc3-interface-module"
    module_id = (
        hb.field(hb.ShortText).default("").desc("Stable ParaDev module identifier.")
    )
    data = (
        hb.field(hb.Json)
        .default({})
        .desc("Structured metadata, localization, and resource references.")
    )
    family = "interface"
    resource_slots = (
        Slot(
            name="assets",
            match="^(interface/.*\\.(gfx|gui)|gfx/interface/.*\\.(dds|tga))$",
            required=True,
            many=True,
            regex=True,
            kind="copy",
        ),
    )
    compilation_hooks = ("normalize", "check", "emit")


def build_family() -> SimpleSourceFamily:
    """Return the Registry compiler owned by this Entity extension."""

    return SimpleSourceFamily(
        family=PIHC3InterfaceModule.family,
        source_slots=PIHC3InterfaceModule.resource_slots,
        copy_path_template="{source_path}",
        visible=False,
    )


__all__ = ["PIHC3InterfaceModule", "build_family"]
