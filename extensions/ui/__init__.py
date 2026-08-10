"""PIHC3 user-interface Entity extension."""

from __future__ import annotations

import heavenbase as hb

from paradev.build import SimpleSourceFamily, Slot


class PIHC3UI(hb.Entity):
    """One independently editable PIHC3 interface resource set."""

    identifier = "pihc3-ui"
    module_id = hb.field(hb.ShortText).default("").desc("Stable ParaDev module identifier.")
    data = hb.field(hb.Json).default({}).desc("Structured metadata and resource references.")
    family = "ui"
    resource_slots = (
        Slot(
            name="layout",
            match="interface/alerts.gui",
            kind="pdx",
        ),
        Slot(
            name="alert_images",
            match=r"^gfx/interface/alerts/.*\.dds$",
            many=True,
            regex=True,
            kind="copy",
            authoring_path="gfx/interface/alerts/{filename}",
        ),
        Slot(
            name="autonomy_images",
            match=r"^gfx/interface/autonomy/.*\.dds$",
            many=True,
            regex=True,
            kind="copy",
            authoring_path="gfx/interface/autonomy/{filename}",
        ),
    )
    compilation_hooks = ("normalize", "check", "emit")


def build_family() -> SimpleSourceFamily:
    """Return the Registry compiler owned by this Entity extension."""

    return SimpleSourceFamily(
        family=PIHC3UI.family,
        source_slots=PIHC3UI.resource_slots,
        pdx_path_template="{source_path}",
        copy_path_template="{source_path}",
    )


__all__ = ["PIHC3UI", "build_family"]
