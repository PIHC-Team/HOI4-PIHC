"""PIHC3 defines Entity extension."""

from __future__ import annotations

import heavenbase as hb

from paradev.build import SimpleSourceFamily, Slot


class PIHC3DefinesModule(hb.Entity):
    """One independently editable PIHC3 defines module."""

    identifier = "pihc3-defines-module"
    module_id = (
        hb.field(hb.ShortText).default("").desc("Stable ParaDev module identifier.")
    )
    data = (
        hb.field(hb.Json)
        .default({})
        .desc("Structured metadata, localization, and resource references.")
    )
    family = "defines"
    resource_slots = (
        Slot(
            name="files",
            match="^common/defines/.*\\.lua$",
            required=True,
            many=True,
            regex=True,
            kind="copy",
            authoring_path="common/defines/{filename}",
        ),
    )
    compilation_hooks = ("normalize", "check", "emit")


def build_family() -> SimpleSourceFamily:
    """Return the Registry compiler owned by this Entity extension."""

    return SimpleSourceFamily(
        family=PIHC3DefinesModule.family,
        source_slots=PIHC3DefinesModule.resource_slots,
        copy_path_template="{source_path}",
        visible=False,
    )


__all__ = ["PIHC3DefinesModule", "build_family"]
