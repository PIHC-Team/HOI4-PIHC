"""PIHC3 text-icon Entity extension."""

from __future__ import annotations

import heavenbase as hb

from paradev.build import SimpleSourceFamily, Slot


class PIHC3TextIcon(hb.Entity):
    """One independently editable PIHC3 text-icon resource set."""

    identifier = "pihc3-texticon"
    module_id = hb.field(hb.ShortText).default("").desc("Stable ParaDev module identifier.")
    data = hb.field(hb.Json).default({}).desc("Structured metadata and resource references.")
    family = "texticon"
    resource_slots = (
        Slot(
            name="definitions",
            match=r"^interface/PIHC_(texticons|unit_categories)\.gfx$",
            many=True,
            regex=True,
            kind="pdx",
        ),
        Slot(
            name="images",
            match=r"^gfx/texticons/.*\.dds$",
            many=True,
            regex=True,
            kind="copy",
            authoring_path="gfx/texticons/{filename}",
        ),
    )
    compilation_hooks = ("normalize", "check", "emit")


def build_family() -> SimpleSourceFamily:
    """Return the Registry compiler owned by this Entity extension."""

    return SimpleSourceFamily(
        family=PIHC3TextIcon.family,
        source_slots=PIHC3TextIcon.resource_slots,
        pdx_path_template="{source_path}",
        copy_path_template="{source_path}",
    )


__all__ = ["PIHC3TextIcon", "build_family"]
